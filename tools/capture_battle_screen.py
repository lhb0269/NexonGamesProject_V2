"""
전투 화면 캡처 도구

게임을 전투 화면으로 진입시킨 후 실행하면 스크린샷을 저장합니다.
저장된 이미지에서 코스트 UI 위치를 측정하세요.
"""

import sys
from pathlib import Path
import time
from datetime import datetime

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.automation.game_controller import GameController


def main():
    print("=" * 70)
    print("전투 화면 캡처 도구")
    print("=" * 70)
    print()
    print("준비사항:")
    print("1. 게임을 전투 화면으로 진입")
    print("2. 코스트 UI가 명확하게 보이는 상태로 대기")
    print("3. 화면이 움직이지 않는 안정된 상태 유지")
    print()

    # 카운트다운
    for i in range(5, 0, -1):
        print(f"캡처까지: {i}초...")
        time.sleep(1)

    print("\n화면 캡처 중...")

    try:
        controller = GameController()
        screenshot = controller.screenshot()

        # 저장 경로
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = project_root / "logs" / "ocr_calibration"
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / f"battle_screen_{timestamp}.png"
        screenshot.save(output_path)

        print(f"✓ 스크린샷 저장 완료: {output_path}")
        print()
        print("다음 단계:")
        print("1. 저장된 이미지를 Paint 또는 이미지 뷰어로 열기")
        print("2. 마우스 커서로 코스트 숫자 영역 측정")
        print("   - 좌측 상단 좌표 (x1, y1) 확인")
        print("   - 우측 하단 좌표 (x2, y2) 확인")
        print("3. config/ocr_regions.py 파일에서 BATTLE_COST_VALUE_REGION 업데이트")
        print()
        print(f"이미지 크기: {screenshot.size[0]}x{screenshot.size[1]}")
        print(f"파일 크기: {output_path.stat().st_size:,} bytes")

    except Exception as e:
        print(f"✗ 캡처 실패: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
