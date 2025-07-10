# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['../main.py'],
    pathex=['../smile', '../python_packages'],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["data", ".git", '.buildozer'],
    noarchive=False,
    optimize=0,
)

a.datas += Tree('../assets', prefix='assets', excludes=['.git', '.buildozer'])
a.datas += Tree('../smile/smile', prefix='smile', excludes=['__pycache__', '*.py', '.git', '.buildozer'])
a.datas += Tree('../tasks', prefix='tasks', excludes=['__pycache__', '.gitignore', '.gitattributes',
                                                                '*.md', '*.py', '.git', '.buildozer'])

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='NIMHCogMood',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='universal2',
    codesign_identity='Developer ID Application: Francisco Machado Aires Pereira (DKN5GQ893X)',
    entitlements_file='./entitlements.plist',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='NIMHCogMood',
)
app = BUNDLE(
    coll,
    name='NIMHCogMood.app',
    icon=None,
    bundle_identifier='gov.nih.nimh.mlc.nimhcogmood',
    info_plist={
        'NSDownloadsFolderUsageDescription': "NIMHCogMood needs to write temporary experiment files to your downloads directory. You can delete them once you've completed the experiment.",
        'NSHighResolutionCapable': 'True',
        'CFBundleDisplayName': 'NIMHCogMood',
        'CFBundleName': 'NIMHCogMood',
        'CFBundleIdentifier': 'gov.nih.nimh.mlc.nimhcogmood',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'LSArchitecturePriority': ['x86_64', 'arm64'],
        'WorkerID': '"------------------------------------------------".---------------------------'
    }
)
