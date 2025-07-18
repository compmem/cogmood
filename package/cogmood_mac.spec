# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

data = [
    ('../brain_load.png', '.'),
    # ('../serverinfo.txt', '.'),
    # ('../cert.pem', '.')
]

a = Analysis(
    ['../main.py'],
    pathex=['../smile', '../python_packages'],
    binaries=[],
    datas=data,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["data", ".git", '.buildozer'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

a.datas += Tree('../assets', prefix='assets', excludes=['.git', '.buildozer'])
a.datas += Tree('../smile/smile', prefix='smile', excludes=['__pycache__', '*.py', '.git', '.buildozer'])
a.datas += Tree('../tasks', prefix='tasks', excludes=['__pycache__', '.gitignore', '.gitattributes',
                                                                '*.md', '*.py', '.git', '.buildozer'])

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='NIMHCogMood',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    target_arch='universal2'
)

app = BUNDLE(
    exe,
    name='NIMHCogMood.app',
    icon=None,
    bundle_identifier='nimh.mlc.nimhcogmood',
    info_plist={
        'NSHighResolutionCapable': 'True',
        'CFBundleDisplayName': 'NIMHCogMood',
        'CFBundleName': 'NIMHCogMood',
        'CFBundleIdentifier': 'nimh.mlc.nimhcogmood',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'LSArchitecturePriority': ['x86_64', 'arm64'],
        'WorkerID': '"------------------------------------------------".---------------------------'
    }
)