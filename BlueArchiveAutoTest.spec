# -*- mode: python ; coding: utf-8 -*-
"""
블루 아카이브 자동화 테스트 실행기 빌드 스펙

PyInstaller를 사용하여 GUI 테스트 러너를 단일 실행 파일로 패키징합니다.

빌드 명령:
    pyinstaller BlueArchiveAutoTest.spec

빌드 결과:
    dist/BlueArchiveAutoTest.exe
"""

from PyInstaller.utils.hooks import collect_data_files, collect_submodules
import os

block_cipher = None

# 프로젝트 루트 경로
project_root = os.path.abspath('.')

# 데이터 파일 수집
datas = [
    ('assets/templates', 'assets/templates'),  # 템플릿 이미지
    ('config', 'config'),  # 설정 파일
    ('src', 'src'),  # 소스 코드 (동적 임포트 대응)
    ('tests', 'tests'),  # 테스트 스크립트
    ('main.py', '.'),  # 메인 스크립트
]

# Hidden imports (동적 임포트 모듈)
hiddenimports = [
    'PIL._tkinter_finder',
    'tkinter',
    'tkinter.ttk',
    'tkinter.scrolledtext',
    'tkinter.messagebox',
    'pyautogui',
    'pytesseract',
    'cv2',
    'numpy',
    'PIL',
    'pathlib',
    'json',
    'datetime',
    'threading',
    'subprocess',
    'io',
    're',
    'time',
    'typing',
]

# OpenCV 하위 모듈 수집
try:
    import cv2
    hiddenimports += collect_submodules('cv2')
except ImportError:
    pass

# src 하위 모듈 자동 수집
hiddenimports += collect_submodules('src')

# 바이너리 수집 (OpenCV DLL 등)
binaries = []
try:
    import cv2
    import os
    cv2_path = os.path.dirname(cv2.__file__)
    # OpenCV DLL 파일 수집
    for file in os.listdir(cv2_path):
        if file.endswith('.dll') or file.endswith('.pyd'):
            binaries.append((os.path.join(cv2_path, file), 'cv2'))
except Exception as e:
    print(f"Warning: Could not collect OpenCV binaries: {e}")

a = Analysis(
    ['gui_test_runner.py'],
    pathex=[project_root],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',  # 불필요한 대형 라이브러리 제외
        'scipy',
        'pandas',
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
    name='BlueArchiveAutoTest',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI 전용 모드 (콘솔 숨김)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 추후 아이콘 추가 가능
)