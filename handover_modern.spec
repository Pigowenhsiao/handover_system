# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
import sys
from PyInstaller.utils.hooks import collect_all

spec_path = Path(globals().get("SPEC", sys.argv[0])).resolve()
project_root = spec_path.parent

matplotlib_datas, matplotlib_binaries, matplotlib_hidden = collect_all("matplotlib")
pandas_datas, pandas_binaries, pandas_hidden = collect_all("pandas")
openpyxl_datas, openpyxl_binaries, openpyxl_hidden = collect_all("openpyxl")

datas = [
    (str(project_root / "frontend" / "public" / "locales"), "frontend/public/locales"),
    (str(project_root / "data" / "master_data.json"), "data"),
]

settings_path = project_root / "handover_settings.json"
if settings_path.exists():
    datas.append((str(settings_path), "."))

datas += matplotlib_datas + pandas_datas + openpyxl_datas
binaries = matplotlib_binaries + pandas_binaries + openpyxl_binaries
hiddenimports = matplotlib_hidden + pandas_hidden + openpyxl_hidden

block_cipher = None


a = Analysis(
    ["handover_system.py"],
    pathex=[str(project_root)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="HandoverSystem",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
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
    name="HandoverSystem",
)

