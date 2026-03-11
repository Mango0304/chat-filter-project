# -*- mode: python ; coding: utf-8 -*-

import os

SPEC_DIR = os.path.abspath(globals().get("SPECPATH", os.getcwd()))
PROJECT_DIR = os.path.abspath(os.path.join(SPEC_DIR, "..", ".."))

a = Analysis(
    [os.path.join(PROJECT_DIR, 'core', 'chat_filter.py')],
    pathex=[PROJECT_DIR, os.path.join(PROJECT_DIR, 'core')],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ChatFilterBinary',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ChatFilterBinary',
)
