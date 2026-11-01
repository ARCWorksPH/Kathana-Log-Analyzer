# -*- mode: python ; coding: utf-8 -*-
# PyInstaller one-file spec for ARCWorks Kathana Log Analyzer 1.0.0 (run via BUILD-PERSONAL.bat)
a = Analysis(['main.py'], pathex=[], binaries=[],
    datas=[('icon.ico', '.'), ('ui', 'ui')],
    hiddenimports=['webview', 'webview.platforms.edgechromium', 'kla_parser'],
    hookspath=[], runtime_hooks=[], excludes=['tests', 'tkinter'], noarchive=False)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, a.binaries, a.datas, [], name='KathanaLogAnalyzer',
    debug=False, strip=False, upx=False, runtime_tmpdir=None, console=False, icon='icon.ico')
