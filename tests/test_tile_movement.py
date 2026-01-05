"""발판 이동 테스트 스크립트

현재 테스트: 임무 개시 → 발판 클릭 (적 유무 판단)
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.recognition.template_matcher import TemplateMatcher
from src.automation.game_controller import GameController
from src.logger.test_logger import TestLogger
from config.settings import ICONS_DIR, UI_DIR, BUTTONS_DIR
import time


def test_tile_movement():
    """발판 이동 테스트 (적 유무 자동 판단)"""
    print("="*60)
    print("발판 이동 테스트")
    print("="*60)

    # 템플릿 경로
    enemy_tile = ICONS_DIR / "enemy_tile.png"
    empty_tile = ICONS_DIR / "empty_tile.png"
    battle_ui = UI_DIR / "battle_ui.png"
    phase_end_button = BUTTONS_DIR / "phase_end_button.png"

    print("\n[템플릿 확인]")
    if not enemy_tile.exists():
        print(f"✗ 적 발판 이미지 없음: {enemy_tile}")
        return False
    else:
        print(f"✓ 적 발판 이미지 존재: {enemy_tile}")

    if not empty_tile.exists():
        print(f"✗ 빈 발판 이미지 없음: {empty_tile}")
        return False
    else:
        print(f"✓ 빈 발판 이미지 존재: {empty_tile}")

    if not battle_ui.exists():
        print(f"✗ 전투 UI 이미지 없음: {battle_ui}")
        return False
    else:
        print(f"✓ 전투 UI 이미지 존재: {battle_ui}")

    if not phase_end_button.exists():
        print(f"✗ Phase 종료 버튼 이미지 없음: {phase_end_button}")
        return False
    else:
        print(f"✓ Phase 종료 버튼 이미지 존재: {phase_end_button}")

    # 낮은 신뢰도로 매처 생성 (0.5)
    matcher = TemplateMatcher(confidence=0.5)
    controller = GameController()
    logger = TestLogger("tile_movement_test")

    print("\n" + "="*60)
    print("테스트 시작")
    print("="*60)
    print("\n게임 화면에서 임무 개시 후 발판이 보이는지 확인하세요.")
    print("10초 후 테스트를 시작합니다...\n")

    # 카운트다운
    for i in range(10, 0, -1):
        print(f"{i}초 남음...")
        time.sleep(1)

    print("\n[1단계] 발판 찾기 (적 우선 탐색)...")
    print("신뢰도: 0.5 (낮은 신뢰도로 테스트)")

    # 1. 먼저 적이 있는 발판 찾기
    enemy_location = matcher.find_template(enemy_tile)
    has_enemy = False
    tile_to_click = None

    if enemy_location:
        print(f"✓ 적이 있는 발판 발견: {enemy_location}")
        has_enemy = True
        tile_to_click = enemy_location
        logger.log_check("발판_탐색", True, f"적 발판 발견: {enemy_location}")
    else:
        print("ℹ 적 발판 없음, 빈 발판 찾는 중...")
        # 2. 적이 없으면 빈 발판 찾기
        empty_location = matcher.find_template(empty_tile)
        if not empty_location:
            print("✗ 이동 가능한 발판을 찾을 수 없습니다")
            logger.log_check("발판_탐색", False, "이동 가능한 발판 없음")
            logger.finalize()
            return False

        print(f"✓ 빈 발판 발견: {empty_location}")
        has_enemy = False
        tile_to_click = empty_location
        logger.log_check("발판_탐색", True, f"빈 발판 발견: {empty_location}")

    # 스크린샷
    screenshot = controller.screenshot()
    logger.save_screenshot(screenshot, "tile_found")

    print(f"\n[2단계] 발판 클릭 {'(적 있음 - 전투 예상)' if has_enemy else '(빈 발판 - 이동만)'}...")
    print("3초 후 클릭합니다...")

    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)

    # 발판 클릭
    try:
        clicked = controller.click_template(tile_to_click, wait_after=2.0)
        if not clicked:
            print("✗ 발판 클릭 실패")
            logger.log_check("발판_클릭", False, "클릭 실패")
            logger.finalize()
            return False

        print("✓ 발판 클릭 성공")
        logger.log_check("발판_클릭", True, "클릭 완료")

        # 스크린샷
        screenshot = controller.screenshot()
        logger.save_screenshot(screenshot, "after_tile_click")

    except Exception as e:
        print(f"✗ 클릭 중 오류: {e}")
        logger.log_check("발판_클릭", False, f"오류: {e}")
        logger.finalize()
        return False

    # 3. 결과 확인
    if has_enemy:
        print("\n[3단계] 전투 진입 확인 중...")
        battle_started = matcher.wait_for_template(battle_ui, timeout=10)

        if battle_started:
            print(f"✓ 전투 UI 출현 확인: {battle_started}")
            logger.log_check("전투_진입", True, "전투 UI 출현")

            # 스크린샷
            screenshot = controller.screenshot()
            logger.save_screenshot(screenshot, "battle_started")

            print("\n" + "="*60)
            print("✓ 테스트 성공!")
            print("="*60)
            print("\n적 발판 클릭 → 전투 진입이 정상적으로 작동합니다.")
        else:
            print("✗ 전투 UI가 10초 내에 나타나지 않음")
            logger.log_check("전투_진입", False, "전투 UI 미출현")

            # 스크린샷
            screenshot = controller.screenshot()
            logger.save_screenshot(screenshot, "battle_ui_timeout")

            print("\n" + "="*60)
            print("✗ 테스트 실패")
            print("="*60)
    else:
        print("\n[3단계] Phase 종료 버튼 찾기...")
        time.sleep(1)  # 이동 완료 대기

        phase_button_location = matcher.find_template(phase_end_button)

        if phase_button_location:
            print(f"✓ Phase 종료 버튼 발견: {phase_button_location}")
            logger.log_check("Phase_종료_버튼_탐색", True, f"위치: {phase_button_location}")

            # 스크린샷
            screenshot = controller.screenshot()
            logger.save_screenshot(screenshot, "phase_end_button_found")

            print("\n[4단계] Phase 종료 버튼 클릭...")
            print("3초 후 클릭합니다...")

            for i in range(3, 0, -1):
                print(f"{i}...")
                time.sleep(1)

            try:
                clicked = controller.click_template(phase_button_location, wait_after=2.0)
                if clicked:
                    print("✓ Phase 종료 버튼 클릭 성공")
                    logger.log_check("Phase_종료", True, "클릭 완료")

                    # 스크린샷
                    screenshot = controller.screenshot()
                    logger.save_screenshot(screenshot, "phase_ended")

                    print("\n" + "="*60)
                    print("✓ 테스트 성공!")
                    print("="*60)
                    print("\n빈 발판 이동 → Phase 종료가 정상적으로 작동합니다.")
                else:
                    print("✗ Phase 종료 버튼 클릭 실패")
                    logger.log_check("Phase_종료", False, "클릭 실패")
            except Exception as e:
                print(f"✗ 클릭 중 오류: {e}")
                logger.log_check("Phase_종료", False, f"오류: {e}")
        else:
            print("✗ Phase 종료 버튼을 찾을 수 없습니다")
            logger.log_check("Phase_종료_버튼_탐색", False, "버튼 미발견")

            # 스크린샷
            screenshot = controller.screenshot()
            logger.save_screenshot(screenshot, "phase_end_button_not_found")

    result_file = logger.finalize()
    print(f"\n결과 파일: {result_file}")
    return True


def main():
    """메인 함수"""
    print("\n블루 아카이브 Normal 1-4 발판 이동 테스트")
    print("\n테스트 범위: 발판 클릭 (적 유무 자동 판단)")
    print("\n준비사항:")
    print("1. 블루 아카이브 게임 실행")
    print("2. Normal 1-4 스테이지에서 임무 개시 후 발판이 보이는 상태")
    print("3. 게임 창이 화면에 보이도록 배치")
    print("\n테스트를 시작합니다...\n")

    test_tile_movement()


if __name__ == "__main__":
    main()
