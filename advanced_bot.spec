# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for ADVANCED-BOT
Creates a standalone executable with all dependencies
"""

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all PySide6 data files
pyside6_datas = collect_data_files('PySide6')

# Collect all playwright data files and modules
playwright_datas = collect_data_files('playwright')
playwright_hiddenimports = collect_submodules('playwright')

# Add example files
added_files = [
    ('example_script.json', '.'),
    ('example_proxies.txt', '.'),
    ('README.md', '.'),
]

# Combine all data files
datas = pyside6_datas + playwright_datas + added_files

# Hidden imports for all dependencies
hiddenimports = [
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'PySide6.QtSvg',
    'playwright',
    'playwright.async_api',
    'playwright.sync_api',
    'playwright._impl',
    'dateutil',
    'aiohttp',
    'asyncio',
    'json',
    'logging',
    'uuid',
    'subprocess',
    'pathlib',
] + playwright_hiddenimports

a = Analysis(
    ['advanced_bot.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ADVANCED-BOT',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Compress executable. Set to False if you encounter issues.
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Keep console for logs
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if available
)
