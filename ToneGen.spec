# -*- mode: python -*-

block_cipher = None


a = Analysis(['ToneGen.py'],
             pathex=['C:\\Users\\Dreser\\PycharmProjects\\ToneGen'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=['matplotlib','scipy','mkl','zmq','alabaster','babel','IPyhton','llnmlite','PyQt4','PyQt5','tk','tcl','h5py','pandas','sklearn','_ssh',],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='ToneGen',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )
