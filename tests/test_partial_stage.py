"""부분 스테이지 테스트 스크립트

준비된 템플릿 이미지만 가지고 단계별로 테스트합니다.

현재 테스트: 시작 발판 → 편성 화면 → 출격 → 스테이지 맵
"""

import sys
import io
from pathlib import Path

# UTF-8 인코딩 강제 설정 (cp949 오류 방지)
# GUI 환경에서는 이미 stdout이 리다이렉션되어 있으므로 스킵
if not hasattr(sys.stdout, '_buffer'):  # GuiOutputStream은 _buffer 속성이 있음
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.recognition.template_matcher import TemplateMatcher
from src.automation.game_controller import GameController
from src.verification.movement_checker import MovementChecker
from src.logger.test_logger import TestLogger
from config.settings import ICONS_DIR, UI_DIR, BUTTONS_DIR, WAIT_SCREEN_TRANSITION


def test_start_to_formation():
    """시작 발판 클릭 → 편성 화면 이동 테스트"""
    print("="*60)
    print("부분 스테이지 테스트: 시작 발판 → 편성 화면")
    print("="*60)

    # 필요한 템플릿 확인
    start_tile = ICONS_DIR / "start_tile.png"
    formation_screen = UI_DIR / "formation_screen.png"

    print("\n[템플릿 확인]")
    if not start_tile.exists():
        print(f"✗ 시작 발판 이미지 없음: {start_tile}")
        print("  → assets/templates/icons/start_tile.png 추가 필요")
        return False
    else:
        print(f"✓ 시작 발판 이미지 존재: {start_tile}")

    if not formation_screen.exists():
        print(f"✗ 편성 화면 이미지 없음: {formation_screen}")
        print("  → assets/templates/ui/formation_screen.png 추가 필요")
        return False
    else:
        print(f"✓ 편성 화면 이미지 존재: {formation_screen}")

    # 초기화
    matcher = TemplateMatcher()
    controller = GameController()
    checker = MovementChecker(matcher, controller)
    logger = TestLogger("partial_stage_test")

    print("\n" + "="*60)
    print("테스트 시작")
    print("="*60)
    print("\n게임 화면에서 시작 발판이 보이는지 확인하세요.")
    print("10초 후 테스트를 시작합니다...\n")

    # 카운트다운
    import time
    for i in range(10, 0, -1):
        print(f"{i}초 남음...")
        time.sleep(1)

    print("\n[1단계] 시작 발판 찾기...")

    # 시작 발판 찾기
    tile_location = matcher.find_template(start_tile)

    if not tile_location:
        print("✗ 시작 발판을 찾을 수 없습니다")
        print("  확인사항:")
        print("  1. 게임 화면에 시작 발판이 보이나요?")
        print("  2. start_tile.png 이미지가 정확한가요?")
        print("  3. 신뢰도(confidence)를 낮춰야 할 수도 있습니다")
        logger.log_check("시작_발판_찾기", False, "시작 발판을 찾을 수 없음")
        logger.finalize()
        return False

    print(f"✓ 시작 발판 발견: {tile_location}")
    logger.log_check("시작_발판_찾기", True, f"위치: {tile_location}")

    # 스크린샷 저장
    screenshot = controller.screenshot()
    logger.save_screenshot(screenshot, "start_tile_found")

    print("\n[2단계] 시작 발판 클릭...")
    print("3초 후 클릭합니다...")

    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)

    # 시작 발판 클릭
    try:
        clicked = controller.click_template(tile_location, wait_after=2.0)
        if clicked:
            print("✓ 시작 발판 클릭 성공")
            logger.log_check("시작_발판_클릭", True, "클릭 완료")
        else:
            print("✗ 시작 발판 클릭 실패")
            logger.log_check("시작_발판_클릭", False, "클릭 실패")
            logger.finalize()
            return False
    except Exception as e:
        print(f"✗ 클릭 중 오류: {e}")
        logger.log_check("시작_발판_클릭", False, f"오류: {e}")
        logger.finalize()
        return False

    print("\n[3단계] 편성 화면 확인...")
    print("편성 화면이 나타날 때까지 대기 중...")

    # 편성 화면 대기
    formation_appeared = matcher.wait_for_template(
        formation_screen,
        timeout=10,
        check_interval=0.5
    )

    if formation_appeared:
        print(f"✓ 편성 화면 출현 확인: {formation_appeared}")
        logger.log_check("편성_화면_확인", True, f"위치: {formation_appeared}")

        # 스크린샷 저장
        screenshot = controller.screenshot()
        logger.save_screenshot(screenshot, "formation_screen_found")

        print("\n" + "="*60)
        print("✓ 테스트 성공!")
        print("="*60)
        print("\n시작 발판 클릭 → 편성 화면 전환이 정상적으로 작동합니다.")

        result_file = logger.finalize()
        print(f"\n결과 파일: {result_file}")
        return True
    else:
        print("✗ 편성 화면이 10초 내에 나타나지 않음")
        print("  확인사항:")
        print("  1. 편성 화면으로 전환되었나요?")
        print("  2. formation_screen.png 이미지가 정확한가요?")

        # 현재 화면 스크린샷 저장
        screenshot = controller.screenshot()
        logger.save_screenshot(screenshot, "formation_screen_timeout")

        logger.log_check("편성_화면_확인", False, "타임아웃 (10초)")

        print("\n" + "="*60)
        print("✗ 테스트 실패")
        print("="*60)

        result_file = logger.finalize()
        print(f"\n결과 파일: {result_file}")
        return False


def test_deploy_to_map(logger):
    """출격 버튼 클릭 → 스테이지 맵 이동 → 임무 개시 버튼 클릭 테스트"""
    print("\n" + "="*60)
    print("출격 → 스테이지 맵 → 임무 개시 테스트")
    print("="*60)

    deploy_button = BUTTONS_DIR / "deploy_button.png"
    stage_map = UI_DIR / "stage_map.png"
    mission_start_button = BUTTONS_DIR / "mission_start_button.png"

    print("\n[템플릿 확인]")
    if not deploy_button.exists():
        print(f"✗ 출격 버튼 이미지 없음: {deploy_button}")
        return False
    else:
        print(f"✓ 출격 버튼 이미지 존재: {deploy_button}")

    if not stage_map.exists():
        print(f"✗ 스테이지 맵 이미지 없음: {stage_map}")
        return False
    else:
        print(f"✓ 스테이지 맵 이미지 존재: {stage_map}")

    if not mission_start_button.exists():
        print(f"✗ 임무 개시 버튼 이미지 없음: {mission_start_button}")
        print("  → assets/templates/buttons/mission_start_button.png 추가 필요")
        return False
    else:
        print(f"✓ 임무 개시 버튼 이미지 존재: {mission_start_button}")

    matcher = TemplateMatcher()
    controller = GameController()

    print("\n[1단계] 출격 버튼 찾기...")
    import time

    # 출격 버튼 찾기
    button_location = matcher.find_template(deploy_button)

    if not button_location:
        print("✗ 출격 버튼을 찾을 수 없습니다")
        logger.log_check("출격_버튼_찾기", False, "출격 버튼을 찾을 수 없음")
        return False

    print(f"✓ 출격 버튼 발견: {button_location}")
    logger.log_check("출격_버튼_찾기", True, f"위치: {button_location}")

    # 스크린샷
    screenshot = controller.screenshot()
    logger.save_screenshot(screenshot, "deploy_button_found")

    print("\n[2단계] 출격 버튼 클릭...")
    print("3초 후 클릭합니다...")

    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)

    # 출격 버튼 클릭
    try:
        clicked = controller.click_template(button_location, wait_after=WAIT_SCREEN_TRANSITION)
        if clicked:
            print("✓ 출격 버튼 클릭 성공")
            logger.log_check("출격_버튼_클릭", True, "클릭 완료")
        else:
            print("✗ 출격 버튼 클릭 실패")
            logger.log_check("출격_버튼_클릭", False, "클릭 실패")
            return False
    except Exception as e:
        print(f"✗ 클릭 중 오류: {e}")
        logger.log_check("출격_버튼_클릭", False, f"오류: {e}")
        return False

    print("\n[3단계] 스테이지 맵 화면 확인...")
    print("스테이지 맵 화면이 나타날 때까지 대기 중...")

    # 스테이지 맵 대기
    map_appeared = matcher.wait_for_template(
        stage_map,
        timeout=10,
        check_interval=0.5
    )

    if not map_appeared:
        print("✗ 스테이지 맵 화면이 10초 내에 나타나지 않음")

        # 현재 화면 스크린샷
        screenshot = controller.screenshot()
        logger.save_screenshot(screenshot, "stage_map_timeout")

        logger.log_check("스테이지_맵_확인", False, "타임아웃 (10초)")
        return False

    print(f"✓ 스테이지 맵 화면 출현 확인: {map_appeared}")
    logger.log_check("스테이지_맵_확인", True, f"위치: {map_appeared}")

    # 스크린샷
    screenshot = controller.screenshot()
    logger.save_screenshot(screenshot, "stage_map_found")

    print("\n[4단계] 임무 개시 버튼 찾기...")
    print("임무 개시 버튼을 찾는 중...")

    # 임무 개시 버튼 찾기
    mission_button_location = matcher.find_template(mission_start_button)

    if not mission_button_location:
        print("✗ 임무 개시 버튼을 찾을 수 없습니다")
        print("  확인사항:")
        print("  1. 스테이지 맵 화면에 임무 개시 버튼이 보이나요?")
        print("  2. mission_start_button.png 이미지가 정확한가요?")
        logger.log_check("임무_개시_버튼_찾기", False, "임무 개시 버튼을 찾을 수 없음")
        return False

    print(f"✓ 임무 개시 버튼 발견: {mission_button_location}")
    logger.log_check("임무_개시_버튼_찾기", True, f"위치: {mission_button_location}")

    # 스크린샷
    screenshot = controller.screenshot()
    logger.save_screenshot(screenshot, "mission_start_button_found")

    print("\n[5단계] 임무 개시 버튼 클릭...")
    print("3초 후 클릭합니다...")

    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)

    # 임무 개시 버튼 클릭
    try:
        clicked = controller.click_template(mission_button_location, wait_after=2.0)
        if clicked:
            print("✓ 임무 개시 버튼 클릭 성공")
            logger.log_check("임무_개시_버튼_클릭", True, "클릭 완료")
        else:
            print("✗ 임무 개시 버튼 클릭 실패")
            logger.log_check("임무_개시_버튼_클릭", False, "클릭 실패")
            return False
    except Exception as e:
        print(f"✗ 클릭 중 오류: {e}")
        logger.log_check("임무_개시_버튼_클릭", False, f"오류: {e}")
        return False

    print("\n" + "="*60)
    print("✓ 출격 → 스테이지 맵 → 임무 개시 성공!")
    print("="*60)
    print("\n이제 발판 이동이 가능한 상태입니다.")
    return True


def main():
    """메인 함수"""
    print("\n블루 아카이브 Normal 1-4 부분 테스트")
    print("\n테스트 범위: 시작 발판 → 편성 화면 → 출격 → 스테이지 맵")
    print("\n준비사항:")
    print("1. 블루 아카이브 게임 실행")
    print("2. Normal 1-4 스테이지 선택 화면에서 대기")
    print("3. 게임 창이 화면에 보이도록 배치")
    print("\n테스트를 시작합니다...\n")

    logger = TestLogger("partial_stage_full_test")

    # 1단계: 시작 발판 → 편성 화면
    success1 = test_start_to_formation()

    if not success1:
        print("\n[1단계 실패] 시작 발판 → 편성 화면")
        print("실패한 단계를 먼저 해결해주세요.")
        print("logs/ 폴더의 스크린샷을 확인하여 문제를 파악할 수 있습니다.")
        return

    print("\n" + "="*60)
    print("1단계 성공! 다음 단계로 진행합니다...")
    print("="*60)

    import time
    time.sleep(2)  # 잠시 대기

    # 2단계: 출격 → 스테이지 맵
    success2 = test_deploy_to_map(logger)

    if not success2:
        print("\n[2단계 실패] 출격 → 스테이지 맵")
        print("실패한 단계를 먼저 해결해주세요.")
        print("logs/ 폴더의 스크린샷을 확인하여 문제를 파악할 수 있습니다.")
        logger.finalize()
        return

    # 전체 성공
    print("\n" + "="*60)
    print("✓ 전체 테스트 성공!")
    print("="*60)
    print("\n완료된 단계:")
    print("1. ✓ 시작 발판 → 편성 화면")
    print("2. ✓ 출격 → 스테이지 맵")
    print("\n다음 단계:")
    print("1. 적 발판 이미지 추가: assets/templates/icons/enemy_tile.png")
    print("2. 전투 UI 이미지 추가: assets/templates/ui/battle_ui.png")
    print("3. 테스트 계속 진행")

    result_file = logger.finalize()
    print(f"\n결과 파일: {result_file}")


if __name__ == "__main__":
    main()
