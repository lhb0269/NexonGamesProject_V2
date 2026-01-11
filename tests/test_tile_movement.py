"""발판 이동 테스트 스크립트

현재 테스트: 임무 개시 → 발판 클릭 (적 유무 판단)
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
from src.verification.battle_checker import BattleChecker
from src.logger.test_logger import TestLogger
from config.settings import ICONS_DIR, BUTTONS_DIR
import time


def check_templates():
    """템플릿 파일 존재 확인"""
    print("\n[템플릿 확인]")

    templates = {
        "enemy_tile.png": "적 발판 이미지",
        "empty_tile.png": "빈 발판 이미지",
        "phase_end_button.png": "Phase 종료 버튼 이미지",
        "character_marker.png": "캐릭터 마커 이미지"
    }

    for filename, description in templates.items():
        if filename.endswith("button.png"):
            filepath = BUTTONS_DIR / filename
        else:
            filepath = ICONS_DIR / filename

        if not filepath.exists():
            print(f"✗ {description} 없음: {filepath}")
            return False
        else:
            print(f"✓ {description} 존재: {filepath}")

    # 마스크 파일 확인 (선택 사항)
    character_marker_mask = ICONS_DIR / "character_marker_mask.png"
    use_mask_file = character_marker_mask.exists()

    if use_mask_file:
        print(f"✓ 캐릭터 마커 마스크 존재: {character_marker_mask}")
        print("  → 외부 마스크 파일 사용")
    else:
        print(f"⚠ 캐릭터 마커 마스크 없음: {character_marker_mask}")
        print("  → 템플릿 알파 채널 또는 일반 템플릿 매칭 사용")

    return True, use_mask_file


def find_character_marker(matcher, use_mask_file, logger):
    """캐릭터 마커 위치 확인"""
    print(f"\n[1단계] 캐릭터 마커 위치 확인...")
    print("신뢰도: 0.6")

    character_marker = ICONS_DIR / "character_marker.png"
    character_marker_mask = ICONS_DIR / "character_marker_mask.png"

    # 마스크 파일이 있으면 사용, 없으면 알파 채널 또는 일반 매칭
    if use_mask_file:
        initial_marker_pos = matcher.find_template_with_mask(character_marker, character_marker_mask)
    else:
        initial_marker_pos = matcher.find_template_with_mask(character_marker)

    character_x = None
    character_y = None

    if not initial_marker_pos:
        logger.log_check("캐릭터_마커_초기_위치", False, "마커 미발견")
        initial_marker_pos = None
        return None,None,None # 마커를 찾지 못했으면 좌표 None 반환
    else:
        character_x = initial_marker_pos[0] + initial_marker_pos[2] // 2
        character_y = (initial_marker_pos[1] + initial_marker_pos[3] // 2) + 250  # 위치 보정
        print(f"✓ 캐릭터 마커 위치: ({character_x}, {character_y})")
        logger.log_check("캐릭터_마커_초기_위치", True, f"위치: ({character_x}, {character_y})")

        # 스크린샷
        controller = GameController()
        screenshot = controller.screenshot()
        logger.save_screenshot(screenshot, "marker_initial_position")

    return initial_marker_pos, character_x, character_y


def is_within_range(tile_location, char_x, char_y, max_distance=300):
    """발판이 캐릭터 주변 반경 내에 있는지 확인"""
    if char_x is None or char_y is None:
        return True  # 캐릭터 위치를 모르면 모든 발판 허용

    tile_center_x = tile_location[0] + tile_location[2] // 2
    tile_center_y = tile_location[1] + tile_location[3] // 2
    distance = ((tile_center_x - char_x) ** 2 + (tile_center_y - char_y) ** 2) ** 0.5
    return distance <= max_distance


def find_nearby_tile(matcher, character_x, character_y, logger):
    """캐릭터 주변 발판 찾기 (적 우선 탐색)"""
    print(f"\n[2단계] 캐릭터 주변 발판 찾기 (적 우선 탐색)...")
    if character_x is not None:
        print(f"  캐릭터 위치: ({character_x}, {character_y})")
        print(f"  탐색 반경: 300픽셀")

    enemy_tile = ICONS_DIR / "enemy_tile.png"
    empty_tile = ICONS_DIR / "empty_tile.png"

    has_enemy = False
    tile_to_click = None

    # 1. 먼저 적이 있는 발판 찾기
    enemy_location = matcher.find_template(enemy_tile)

    if enemy_location and is_within_range(enemy_location, character_x, character_y):
        print(f"✓ 캐릭터 주변 적 발판 발견: {enemy_location}")
        has_enemy = True
        tile_to_click = enemy_location
        logger.log_check("발판_탐색", True, f"적 발판 발견: {enemy_location}")
    else:
        if enemy_location:
            print(f"ℹ 적 발판이 있지만 캐릭터 주변 범위 밖: {enemy_location}")
        else:
            print("ℹ 적 발판 없음")

        # 2. 적이 없거나 범위 밖이면 빈 발판 찾기
        print("  → 빈 발판 찾는 중...")
        empty_location = matcher.find_template(empty_tile)

        if empty_location and is_within_range(empty_location, character_x, character_y):
            print(f"✓ 캐릭터 주변 빈 발판 발견: {empty_location}")
            has_enemy = False
            tile_to_click = empty_location
            logger.log_check("발판_탐색", True, f"빈 발판 발견: {empty_location}")
        else:
            if empty_location:
                print(f"✗ 빈 발판이 있지만 캐릭터 주변 범위 밖: {empty_location}")
            else:
                print("✗ 빈 발판 없음")
            logger.log_check("발판_탐색", False, "캐릭터 주변에 이동 가능한 발판 없음")
            return None, None

    # 스크린샷
    controller = GameController()
    screenshot = controller.screenshot()
    logger.save_screenshot(screenshot, "tile_found")

    return has_enemy, tile_to_click


def click_tile(controller, tile_to_click, has_enemy, logger):
    """발판 클릭"""
    print(f"\n[3단계] 발판 클릭 {'(적 있음 - 전투 예상)' if has_enemy else '(빈 발판 - 이동만)'}...")
    print("1초 후 클릭합니다...")
    time.sleep(1)

    try:
        clicked = controller.click_template(tile_to_click, wait_after=0.5)
        if not clicked:
            print("✗ 발판 클릭 실패")
            logger.log_check("발판_클릭", False, "클릭 실패")
            return False

        print("✓ 발판 클릭 성공")
        logger.log_check("발판_클릭", True, "클릭 완료")

        # 스크린샷
        screenshot = controller.screenshot()
        logger.save_screenshot(screenshot, "after_tile_click")

        return True

    except Exception as e:
        print(f"✗ 클릭 중 오류: {e}")
        logger.log_check("발판_클릭", False, f"오류: {e}")
        return False


def verify_character_moved(matcher, use_mask_file, initial_marker_pos, logger):
    """캐릭터 이동 확인 (마커 위치 변경 검증)"""
    if initial_marker_pos is None:
        return True  # 마커를 찾지 못했으면 검증 스킵

    print("\n[3.5단계] 캐릭터 이동 확인 중...")

    character_marker = ICONS_DIR / "character_marker.png"
    character_marker_mask = ICONS_DIR / "character_marker_mask.png"

    # 새로운 마커 위치 찾기 (마스크 파일 또는 알파 채널 사용)
    if use_mask_file:
        final_marker_pos = matcher.find_template_with_mask(character_marker, character_marker_mask)
    else:
        final_marker_pos = matcher.find_template_with_mask(character_marker)

    if not final_marker_pos:
        print("⚠ 이동 후 캐릭터 마커를 찾을 수 없습니다.")
        logger.log_check("캐릭터_이동_확인", False, "이동 후 마커 미발견")
        return True  # 실패해도 테스트 계속 진행

    final_x = final_marker_pos[0] + final_marker_pos[2] // 2
    final_y = final_marker_pos[1] + final_marker_pos[3] // 2
    print(f"✓ 캐릭터 마커 이동 후 위치: ({final_x}, {final_y})")

    # 이동 거리 계산
    initial_x = initial_marker_pos[0] + initial_marker_pos[2] // 2
    initial_y = initial_marker_pos[1] + initial_marker_pos[3] // 2
    distance_moved = ((final_x - initial_x) ** 2 + (final_y - initial_y) ** 2) ** 0.5

    print(f"이동 거리: {distance_moved:.2f} 픽셀")

    # 스크린샷
    controller = GameController()
    screenshot = controller.screenshot()
    logger.save_screenshot(screenshot, "marker_final_position")

    # 이동 여부 판단 (최소 10픽셀 이상 이동)
    if distance_moved >= 10:
        print(f"✓ 캐릭터 이동 확인 성공! (거리: {distance_moved:.2f}px)")
        logger.log_check("캐릭터_이동_확인", True,
                        f"이동 거리: {distance_moved:.2f}px, 시작: ({initial_x}, {initial_y}), 종료: ({final_x}, {final_y})")
        return True
    else:
        print(f"✗ 캐릭터가 이동하지 않은 것으로 보입니다 (거리: {distance_moved:.2f}px)")
        logger.log_check("캐릭터_이동_확인", False, f"이동 거리 부족: {distance_moved:.2f}px")
        return True  # 실패해도 테스트 계속 진행


def verify_battle_entry(battle_checker, logger):
    """전투 진입 확인 (다중 조건 검증)"""
    print("\n[4단계] 전투 진입 확인 중 (다중 조건 검증)...")
    print("  - battle_ui.png, stage_info_ui.png, pause_button.png 확인")
    print("  - 3개 중 2개 이상 인식되면 전투 진입 성공")

    battle_result = battle_checker.verify_battle_entry_multi_condition(
        timeout=15,
        required_matches=2
    )

    controller = GameController()

    if battle_result["success"]:
        print(f"✓ 전투 진입 확인 성공")
        print(f"  매칭된 조건: {battle_result['match_count']}/3개")
        print(f"  조건별 결과: {battle_result['conditions_met']}")
        logger.log_check("전투_진입", True, f"다중 조건 검증 성공 ({battle_result['match_count']}/3)")

        # 스크린샷
        screenshot = controller.screenshot()
        logger.save_screenshot(screenshot, "battle_started")

        print("\n" + "="*60)
        print("✓ 테스트 성공!")
        print("="*60)
        print("\n적 발판 클릭 → 전투 진입이 정상적으로 작동합니다.")
        return True
    else:
        print(f"✗ 전투 진입 확인 실패: {battle_result['message']}")
        print(f"  매칭된 조건: {battle_result['match_count']}/3개")
        print(f"  조건별 결과: {battle_result['conditions_met']}")
        logger.log_check("전투_진입", False, f"다중 조건 검증 실패 ({battle_result['match_count']}/3)")

        # 스크린샷
        screenshot = controller.screenshot()
        logger.save_screenshot(screenshot, "battle_entry_failed")

        print("\n" + "="*60)
        print("✗ 테스트 실패")
        print("="*60)
        return False


def test_tile_movement():
    """발판 이동 테스트 (적 유무 자동 판단)"""
    print("="*60)
    print("발판 이동 테스트")
    print("="*60)

    # 템플릿 확인
    template_check_result = check_templates()
    if template_check_result is False:
        return False

    templates_ok, use_mask_file = template_check_result
    if not templates_ok:
        return False

    print("\n[다중 조건 전투 검증]")
    print("전투 진입은 BattleChecker의 다중 조건 검증을 사용합니다:")
    print("  - battle_ui.png")
    print("  - stage_info_ui.png")
    print("  - pause_button.png")
    print("  (3개 중 2개 이상 인식 시 전투 진입으로 판단)")

    # 매처 및 컨트롤러 생성
    matcher = TemplateMatcher(confidence=0.6)
    controller = GameController()
    battle_checker = BattleChecker(matcher, controller)
    logger = TestLogger("tile_movement_test")

    print("\n" + "="*60)
    print("테스트 시작")
    print("="*60)
    print("\n게임 화면에서 임무 개시 후 발판이 보이는지 확인하세요.")
    print("1초 후 테스트를 시작합니다...\n")
    time.sleep(1)

    # [1단계] 캐릭터 마커 위치 확인
    initial_marker_pos, character_x, character_y = find_character_marker(matcher, use_mask_file, logger)

    # [2단계] 캐릭터 주변 발판 찾기
    has_enemy, tile_to_click = find_nearby_tile(matcher, character_x, character_y, logger)

    if tile_to_click is None:
        logger.finalize()
        return False

    # [3단계] 발판 클릭
    if not click_tile(controller, tile_to_click, has_enemy, logger):
        logger.finalize()
        return False

    # [3.5단계] 캐릭터 이동 확인
    verify_character_moved(matcher, use_mask_file, initial_marker_pos, logger)

    # [4단계] 전투 진입 확인
    result = verify_battle_entry(battle_checker, logger)

    result_file = logger.finalize()
    print(f"\n결과 파일: {result_file}")
    return result


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
