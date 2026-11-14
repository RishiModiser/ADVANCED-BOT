# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['humanexbot_v5.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets/humanex_logo.svg', 'assets'),
        ('assets/humanex_bot_v5.svg', 'assets'),
        ('assets/humanex_bot_v5.ico', 'assets'),
        ('version.json', '.'),
        ('requirements.txt', '.'),
        ('license_config.example.json', '.'),
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
    name='humanexbot_v5',
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
