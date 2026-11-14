# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules

browser_data = []
if Path('playwright-browsers').exists():
    browser_data.append(('playwright-browsers', 'playwright-browsers'))

a = Analysis(
    ['humanexbot_v5.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets/humanex_bot_v5.svg', 'assets'),
        ('assets/humanex_bot_v5.ico', 'assets'),
        ('version.json', '.'),
        ('requirements.txt', '.'),
        ('license_config.example.json', '.'),
        *browser_data,
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'playwright',
        'playwright.async_api',
        'playwright.sync_api',
        'playwright._impl',
        'dateutil',
        'aiohttp',
        'activation_dialog',
        'license_client',
        'startup_diagnostics',
        'app_runtime',
        *collect_submodules('PySide6'),
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='HumanexBot',
    debug=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/humanex_bot_v5.ico',
)
