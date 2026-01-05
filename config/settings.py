"""프로젝트 설정 파일"""

import os
from pathlib import Path

# 프로젝트 루트 디렉토리
PROJECT_ROOT = Path(__file__).parent.parent

# 디렉토리 경로
ASSETS_DIR = PROJECT_ROOT / "assets"
TEMPLATES_DIR = ASSETS_DIR / "templates"
BUTTONS_DIR = TEMPLATES_DIR / "buttons"
ICONS_DIR = TEMPLATES_DIR / "icons"
UI_DIR = TEMPLATES_DIR / "ui"
LOGS_DIR = PROJECT_ROOT / "logs"

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
