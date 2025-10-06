# -*- mode: python ; coding: utf-8 -*-
import os
from pathlib import Path

block_cipher = None

# Detecta caminho do VLC
vlc_path = Path('C:/Program Files/VideoLAN/VLC')
if not vlc_path.exists():
    vlc_path = Path('C:/Program Files (x86)/VideoLAN/VLC')

# Binários do VLC
vlc_binaries = []
if vlc_path.exists():
    vlc_binaries = [
        (str(vlc_path / 'libvlc.dll'), '.'),
        (str(vlc_path / 'libvlccore.dll'), '.'),
    ]

# Plugins do VLC
vlc_plugins = []
if (vlc_path / 'plugins').exists():
    vlc_plugins = [(str(vlc_path / 'plugins'), 'plugins')]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=vlc_binaries,
    datas=[
        ('icons', 'icons'),
        ('config.py', '.'),
        ('ui_elements.py', '.'),
        ('styles.py', '.'),
        ('video_player.py', '.'),
        ('utils.py', '.'),
        ('playlist.py', '.'),
        ('zoom.py', '.'),
        ('settings.py', '.'),
        ('croqui_modal.py', '.'),
    ] + vlc_plugins,
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'PySide6.QtMultimedia',
        'PySide6.QtMultimediaWidgets',
        'vlc',
        'requests',
        'asyncio',
        'subprocess',
        'zipfile',
        'tempfile',
        'ctypes',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'PIL',
        'tkinter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PPL Player',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # False = Sem janela de console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='Icon.ico' if os.path.exists('Icon.ico') else None,
)
