# -*- mode: python ; coding: utf-8 -*-

from kivy_deps import sdl2, glew
block_cipher = None

data = [
    #('..\\brain_load.png', '.'),
    #('..\\serverinfo.txt', '.'),
    #('..\\cert.pem', '.')
    #('..\\pylsl\\lib\\lsl.dll', 'pylsl\\lib\\')
]

a = Analysis(['..\\main.py'],
             pathex=[''],
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
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

a.datas += Tree('..\\assets', prefix='assets', excludes=['.git', '.buildozer'])
a.datas += Tree('..\\smile\\smile', prefix='smile', excludes=['__pycache__', '*.py', '.git', '.buildozer'])
a.datas += Tree('..\\tasks', prefix='tasks', excludes=['__pycache__', '.gitignore', '.gitattributes',
                                                                '*.md', '*.py', '.git', '.buildozer'])

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
          name='test',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None,
          version='exe_versioning.txt' 
        )
