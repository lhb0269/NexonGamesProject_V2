"""블루 아카이브 자동화 테스트 메인 스크립트

GUI 테스트 러너 실행
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# GUI 테스트 러너 임포트
from gui_test_runner import main as gui_main


if __name__ == "__main__":
    # GUI 테스트 러너 실행
    gui_main()
