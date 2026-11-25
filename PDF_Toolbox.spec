# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('resources', 'resources')],
    hiddenimports=['pikepdf', 'PIL', 'PIL.Image', 'pypdf', 'img2pdf', 'pikepdf._core', 'fitz', 'PySide6.QtSvg', 'pytesseract', 'pdf2docx', 'pdfplumber', 'openpyxl', 'reportlab', 'reportlab.pdfbase.ttfonts', 'reportlab.pdfgen.canvas', 'bidi', 'bidi.algorithm'],
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
    a.binaries,
    a.datas,
    [],
    name='PDF_Toolbox',
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
    icon=['resources\\icons\\app.ico'],
)
