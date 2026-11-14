#!/usr/bin/env python3
"""Render the complete HumanexBot GUI to a visual PDF."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# Allow PDF generation on build machines without a display server.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QMarginsF, QSize, Qt
from PySide6.QtGui import QPageLayout, QPageSize, QPainter, QPdfWriter
from PySide6.QtWidgets import QApplication, QScrollArea

from humanexbot_v5 import AppGUI


SECTION_NAMES = (
    "Website Traffic",
    "Traffic Behaviour",
    "Proxy Settings",
    "RPA Script Creator",
    "Control",
    "Logs",
)


def _expand_scrollable_page(page: QScrollArea, width: int) -> int:
    """Make a scrollable page's complete content available for rendering."""
    content = page.widget()
    if content is None:
        return page.sizeHint().height()

    content.setMinimumWidth(max(1, width))
    content.adjustSize()
    content_height = max(content.sizeHint().height(), content.height())
    page.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    page.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    page.setMinimumHeight(content_height + 2)
    page.resize(width, content_height + 2)
    return content_height + 2


def _prepare_window(window: AppGUI, section_index: int) -> None:
    """Select a section and resize the window so no section content is clipped."""
    window.stacked_widget.setCurrentIndex(section_index)
    QApplication.processEvents()

    page = window.stacked_widget.currentWidget()
    content_height = page.sizeHint().height()
    if isinstance(page, QScrollArea):
        content_width = max(900, window.width() - window.sidebar.width() - 24)
        content_height = _expand_scrollable_page(page, content_width)

    window.resize(QSize(1440, max(900, content_height + 24)))
    window.adjustSize()
    QApplication.processEvents()


def generate_pdf(output_path: Path) -> int:
    """Generate a PDF containing every main GUI section."""
    app = QApplication.instance() or QApplication(sys.argv[:1])
    app.setStyle("Fusion")

    window = AppGUI()
    window.resize(1440, 900)
    window.show()
    QApplication.processEvents()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    writer = QPdfWriter(str(output_path))
    writer.setResolution(144)
    writer.setPageLayout(
        QPageLayout(
            QPageSize(QPageSize.PageSizeId.A4),
            QPageLayout.Orientation.Landscape,
            QMarginsF(12, 12, 12, 12),
        )
    )

    painter = QPainter(writer)
    try:
        for index, name in enumerate(SECTION_NAMES):
            _prepare_window(window, index)
            image = window.grab().toImage()
            if image.isNull():
                raise RuntimeError(f"Could not render GUI section: {name}")

            page_rect = writer.pageLayout().paintRectPixels(writer.resolution())
            scale = min(
                page_rect.width() / image.width(),
                page_rect.height() / image.height(),
            )
            target_size = QSize(
                max(1, int(image.width() * scale)),
                max(1, int(image.height() * scale)),
            )
            target = page_rect
            target.setSize(target_size)
            target.moveCenter(page_rect.center())
            painter.drawImage(target, image)
            if index < len(SECTION_NAMES) - 1:
                writer.newPage()
    finally:
        painter.end()
        window.close()
        window.deleteLater()
        QApplication.processEvents()

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Render all main HumanexBot GUI sections to a visual PDF."
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("humanexbot_gui.pdf"),
        help="PDF output path (default: humanexbot_gui.pdf)",
    )
    args = parser.parse_args()

    try:
        return generate_pdf(args.output.resolve())
    except Exception as exc:
        print(f"GUI PDF generation failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
