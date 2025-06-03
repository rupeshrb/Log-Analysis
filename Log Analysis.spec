# -*- mode: python ; coding: utf-8 -*-

import sys  
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Increase recursion limit for PyInstaller
sys.setrecursionlimit(sys.getrecursionlimit() * 5)

# Get all custom widget modules
custom_widget_modules = collect_submodules('Custom_Widgets')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Be explicit about file patterns to ensure all files are included
        ('assets/html/*.html', 'assets/html'),
        ('assets/css/*.css', 'assets/css'),
        ('assets/js/*.js', 'assets/js'),
        ('icons/*.svg', 'icons'),
        ('Qss/*', 'Qss'),  # Include all files in Qss directory
        ('log.ico', '.'),
        ('style.json', '.'),
        ('models/*.joblib', 'models'),
        ('collected_logs', 'collected_logs'),
    ],
    hiddenimports=[
        # Standard libraries
        'setuptools',
        'setuptools._distutils',
        'setuptools._distutils.version',
        'setuptools._distutils.command',
        'setuptools._distutils.command.build',
        'setuptools._vendor',
        'setuptools._distutils.compilers',
        'pkg_resources.py2_warn',
        'sqlite3',
        'threading',
        'datetime',
        'json',
        'math',
        'pathlib',
        'ipaddress',
        'base64',
        're',
        'concurrent.futures',
        'platform',
        'subprocess',
        'logging',
        'winsound',
        
        # PySide6 modules - be more explicit
        'PySide6',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'PySide6.QtWebEngineWidgets',
        'PySide6.QtWebEngineCore',
        'PySide6.QtWebChannel',
        'PySide6.QtUiTools',  # Add this for UI loading
        'PySide6.QtSvg',      # Add this for SVG support
        'PySide6.QtNetwork',  # Add this for network operations
        
        # Data science libraries
        'sklearn',
        'sklearn.ensemble',
        'sklearn.feature_extraction',
        'sklearn.feature_extraction.text',
        'sklearn.pipeline',
        'sklearn.model_selection',
        'numpy',
        'pandas',
        'joblib',
        'psutil',
        
        # Custom modules - include all Custom_Widgets submodules
        'assets.py.home',
        'assets.py.log',
        'assets.py.system_analysis',
        'Custom_Widgets',
        'Custom_Widgets.QCustomQStackedWidget',
        'Custom_Widgets.QCustomSlideMenu',
        'Custom_Widgets.JSonStyles',
    ] + custom_widget_modules,  # Add all discovered Custom_Widgets submodules
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PyQt5', 'PySide2'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
    optimize=0,
)

# Add runtime hooks to ensure proper initialization of QtWebEngineProcess
a.datas += [('qt.conf', '.', 'DATA')]

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Log Analysis',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Change to True temporarily for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['log.ico'],
)