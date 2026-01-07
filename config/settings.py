"""프로젝트 설정 파일"""

import os
import json
from pathlib import Path

# 프로젝트 루트 디렉토리
PROJECT_ROOT = Path(__file__).parent.parent

# 디렉토리 경로
ASSETS_DIR = PROJECT_ROOT / "assets"
TEMPLATES_DIR = ASSETS_DIR / "templates"
LOGS_DIR = PROJECT_ROOT / "logs"

# 해상도 설정 파일
SETTINGS_FILE = PROJECT_ROOT / "config" / "display_settings.json"

# 지원하는 해상도 목록
SUPPORTED_RESOLUTIONS = {
    "1920x1080": {"width": 1920, "height": 1080, "name": "Full HD (1920x1080)"},
    "2560x1440": {"width": 2560, "height": 1440, "name": "QHD (2560x1440)"},
    "3840x2160": {"width": 3840, "height": 2160, "name": "4K UHD (3840x2160)"},
}

# 현재 해상도 설정 로드
def load_display_settings():
    """디스플레이 설정 로드"""
    if SETTINGS_FILE.exists():
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            settings = json.load(f)
            return settings.get('resolution', '1920x1080')
    return '1920x1080'  # 기본값

def save_display_settings(resolution):
    """디스플레이 설정 저장"""
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump({'resolution': resolution}, f, indent=2, ensure_ascii=False)

# 현재 설정된 해상도
CURRENT_RESOLUTION = load_display_settings()

# 해상도별 템플릿 디렉토리
def get_resolution_dir(resolution=None):
    """해상도별 템플릿 디렉토리 반환"""
    if resolution is None:
        resolution = CURRENT_RESOLUTION
    return TEMPLATES_DIR / resolution

# 현재 해상도의 템플릿 디렉토리
RESOLUTION_DIR = get_resolution_dir()
BUTTONS_DIR = RESOLUTION_DIR / "buttons"
ICONS_DIR = RESOLUTION_DIR / "icons"
UI_DIR = RESOLUTION_DIR / "ui"

# 템플릿 매칭 설정
TEMPLATE_MATCHING_CONFIDENCE = 0.8  # 신뢰도 임계값
TEMPLATE_MATCHING_RETRY = 3  # 재시도 횟수
TEMPLATE_MATCHING_TIMEOUT = 30  # 타임아웃 (초)

# 대기 시간 설정 (초)
WAIT_SCREEN_TRANSITION = 1.5  # 화면 전환 대기
WAIT_ANIMATION = 0.8  # 애니메이션 대기
WAIT_BATTLE_LOADING = 4.0  # 전투 로딩 대기
WAIT_SKILL_COOLDOWN = 0.3  # 스킬 쿨다운 확인 간격

# 스킬 사용 관련
SKILL_CHECK_INTERVAL = 0.5  # 스킬 사용 가능 확인 간격
MAX_SKILL_WAIT_TIME = 30  # 스킬 사용 최대 대기 시간

# 로그 설정
LOG_LEVEL = "INFO"
SAVE_SCREENSHOTS_ON_ERROR = True
SCREENSHOT_FORMAT = "png"
