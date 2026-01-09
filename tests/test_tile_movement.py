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


def test_tile_movement():
    """발판 이동 테스트 (적 유무 자동 판단)"""
    print("="*60)
    print("발판 이동 테스트")
    print("="*60)

    # 템플릿 경로
    enemy_tile = ICONS_DIR / "enemy_tile.png"
    empty_tile = ICONS_DIR / "empty_tile.png"
    phase_end_button = BUTTONS_DIR / "phase_end_button.png"
    character_marker = ICONS_DIR / "character_marker.png"
    character_marker_mask = ICONS_DIR / "character_marker_mask.png"

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

    if not phase_end_button.exists():
        print(f"✗ Phase 종료 버튼 이미지 없음: {phase_end_button}")
        return False
    else:
        print(f"✓ Phase 종료 버튼 이미지 존재: {phase_end_button}")

    if not character_marker.exists():
        print(f"✗ 캐릭터 마커 이미지 없음: {character_marker}")
        return False
    else:
        print(f"✓ 캐릭터 마커 이미지 존재: {character_marker}")

    # 마스크 파일 확인 (선택 사항)
    use_mask_file = character_marker_mask.exists()
    if use_mask_file:
        print(f"✓ 캐릭터 마커 마스크 존재: {character_marker_mask}")
        print("  → 외부 마스크 파일 사용")
    else:
        print(f"⚠ 캐릭터 마커 마스크 없음: {character_marker_mask}")
        print("  → 템플릿 알파 채널 또는 일반 템플릿 매칭 사용")

    print("\n[다중 조건 전투 검증]")
    print("전투 진입은 BattleChecker의 다중 조건 검증을 사용합니다:")
    print("  - battle_ui.png")
    print("  - stage_info_ui.png")
    print("  - pause_button.png")
    print("  (3개 중 2개 이상 인식 시 전투 진입으로 판단)")

    # 낮은 신뢰도로 매처 생성 (0.6)
    matcher = TemplateMatcher(confidence=0.6)
    controller = GameController()
    battle_checker = BattleChecker(matcher, controller)
    logger = TestLogger("tile_movement_test")

    print("\n" + "="*60)
    print("테스트 시작")
    print("="*60)
    print("\n게임 화면에서 임무 개시 후 발판이 보이는지 확인하세요.")
    print("3초 후 테스트를 시작합니다...\n")

    # 카운트다운
    for i in range(3, 0, -1):
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

    # 캐릭터 마커 초기 위치 확인
    print(f"\n[1.5단계] 캐릭터 마커 초기 위치 확인...")

    # 마스크 파일이 있으면 사용, 없으면 알파 채널 또는 일반 매칭
    # find_template_with_mask()는 자동으로 알파 채널을 마스크로 사용함
    if use_mask_file:
        initial_marker_pos = matcher.find_template_with_mask(character_marker, character_marker_mask)
    else:
        # 투명 PNG의 경우 알파 채널을 자동으로 마스크로 사용
        initial_marker_pos = matcher.find_template_with_mask(character_marker)

    if not initial_marker_pos:
        print("⚠ 캐릭터 마커를 찾을 수 없습니다. 위치 변경 검증을 건너뜁니다.")
        logger.log_check("캐릭터_마커_초기_위치", False, "마커 미발견")
        initial_marker_pos = None
    else:
        initial_x = initial_marker_pos[0] + initial_marker_pos[2] // 2
        initial_y = initial_marker_pos[1] + initial_marker_pos[3] // 2
        print(f"✓ 캐릭터 마커 초기 위치: ({initial_x}, {initial_y})")
        logger.log_check("캐릭터_마커_초기_위치", True, f"위치: ({initial_x}, {initial_y})")

        # 스크린샷
        screenshot = controller.screenshot()
        logger.save_screenshot(screenshot, "marker_initial_position")

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

        # 캐릭터 이동 확인 (마커 위치 변경 검증)
        if initial_marker_pos is not None:
            print("\n[2.5단계] 캐릭터 이동 확인 중...")
            print("이동 애니메이션 대기 (3초)...")
            time.sleep(3)  # 이동 애니메이션 대기

            # 새로운 마커 위치 찾기 (마스크 파일 또는 알파 채널 사용)
            if use_mask_file:
                final_marker_pos = matcher.find_template_with_mask(character_marker, character_marker_mask)
            else:
                # 투명 PNG의 경우 알파 채널을 자동으로 마스크로 사용
                final_marker_pos = matcher.find_template_with_mask(character_marker)

            if not final_marker_pos:
                print("⚠ 이동 후 캐릭터 마커를 찾을 수 없습니다.")
                logger.log_check("캐릭터_이동_확인", False, "이동 후 마커 미발견")
            else:
                final_x = final_marker_pos[0] + final_marker_pos[2] // 2
                final_y = final_marker_pos[1] + final_marker_pos[3] // 2
                print(f"✓ 캐릭터 마커 이동 후 위치: ({final_x}, {final_y})")

                # 이동 거리 계산
                initial_x = initial_marker_pos[0] + initial_marker_pos[2] // 2
                initial_y = initial_marker_pos[1] + initial_marker_pos[3] // 2
                distance_moved = ((final_x - initial_x) ** 2 + (final_y - initial_y) ** 2) ** 0.5

                print(f"이동 거리: {distance_moved:.2f} 픽셀")

                # 스크린샷
                screenshot = controller.screenshot()
                logger.save_screenshot(screenshot, "marker_final_position")

                # 이동 여부 판단 (최소 10픽셀 이상 이동)
                if distance_moved >= 10:
                    print(f"✓ 캐릭터 이동 확인 성공! (거리: {distance_moved:.2f}px)")
                    logger.log_check("캐릭터_이동_확인", True, f"이동 거리: {distance_moved:.2f}px, 시작: ({initial_x}, {initial_y}), 종료: ({final_x}, {final_y})")
                else:
                    print(f"✗ 캐릭터가 이동하지 않은 것으로 보입니다 (거리: {distance_moved:.2f}px)")
                    logger.log_check("캐릭터_이동_확인", False, f"이동 거리 부족: {distance_moved:.2f}px")

    except Exception as e:
        print(f"✗ 클릭 중 오류: {e}")
        logger.log_check("발판_클릭", False, f"오류: {e}")
        logger.finalize()
        return False

    # 3. 결과 확인
    if has_enemy:
        print("\n[3단계] 전투 진입 확인 중 (다중 조건 검증)...")
        print("  - battle_ui.png, stage_info_ui.png, pause_button.png 확인")
        print("  - 3개 중 2개 이상 인식되면 전투 진입 성공")

        battle_result = battle_checker.verify_battle_entry_multi_condition(
            timeout=15,
            required_matches=2
        )

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
