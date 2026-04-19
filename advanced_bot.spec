# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['advanced_bot.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('example_script.json', '.'),
        ('example_proxies.txt', '.'),
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
    name='advanced_bot',
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
)
