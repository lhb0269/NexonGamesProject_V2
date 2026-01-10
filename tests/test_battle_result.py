"""전투 결과 확인 테스트 스크립트

현재 테스트: Victory 화면 → 통계 버튼 → 데미지 기록 → 랭크 획득 → 스테이지 복귀
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
from src.logger.test_logger import TestLogger
from config.settings import BUTTONS_DIR, UI_DIR
import time


def check_templates():
    """템플릿 파일 존재 확인"""
    print("\n[템플릿 확인]")

    templates = {
        "Victory 화면": UI_DIR / "victory.png",
        "통계 버튼": BUTTONS_DIR / "battle_log_button.png",
        "데미지 기록 창": UI_DIR / "damage_report.png",
        "데미지 기록 확인 버튼": BUTTONS_DIR / "battle_log_confirm_button.png",
        "Victory 확인 버튼": BUTTONS_DIR / "victory_confirm.png",
        "랭크 획득 창": UI_DIR / "rank_reward.png",
        "랭크 획득 창 확인 버튼": BUTTONS_DIR / "rank_reward_confirm_button.png",
        "스테이지 맵": UI_DIR / "stage_map_2.png"
    }

    missing_templates = []
    for name, path in templates.items():
        if not path.exists():
            print(f"✗ {name} 이미지 없음: {path}")
            missing_templates.append(name)
        else:
            print(f"✓ {name} 이미지 존재: {path}")

    # 학생별 데미지 템플릿 확인 (선택 사항)
    print("\n[학생별 데미지 템플릿 확인]")
    student_template_count = 0
    for i in range(1, 7):
        student_icon = UI_DIR / f"student_icon_{i}.png"

        if student_icon.exists():
            print(f"✓ 학생_{i} 아이콘 존재")
            student_template_count += 1

    if student_template_count == 0:
        print("  (학생 템플릿이 없으면 학생별 데미지 검증이 스킵됩니다)")

    if missing_templates:
        print(f"\n⚠ 누락된 필수 템플릿: {', '.join(missing_templates)}")
        print("테스트를 계속 진행하지만 해당 단계에서 실패할 수 있습니다.")

    return templates


def verify_victory_screen(matcher, controller, logger):
    """1단계: Victory 화면 확인"""
    print("\n[1단계] Victory 화면 확인...")

    victory_screen = UI_DIR / "victory.png"
    victory_found = matcher.find_template(victory_screen)

    if victory_found:
        print(f"✓ Victory 화면 발견: {victory_found}")
        logger.log_check("Victory_화면_확인", True, f"위치: {victory_found}")

        screenshot = controller.screenshot()
        logger.save_screenshot(screenshot, "victory_screen_found")
        return True
    else:
        print("✗ Victory 화면을 찾을 수 없습니다")
        print("  확인사항:")
        print("  1. 게임이 Victory 화면에 있나요?")
        print("  2. victory.png 이미지가 정확한가요?")
        logger.log_check("Victory_화면_확인", False, "Victory 화면 미발견")
        return False


def click_battle_log_button(matcher, controller, logger):
    """2-3단계: 통계 버튼 찾기 및 클릭"""
    print("\n[2단계] 통계 버튼 찾기...")

    battle_log_button = BUTTONS_DIR / "battle_log_button.png"
    stats_button_location = matcher.find_template(battle_log_button)

    if not stats_button_location:
        print("✗ 통계 버튼을 찾을 수 없습니다")
        logger.log_check("통계_버튼_찾기", False, "통계 버튼 미발견")
        return False

    print(f"✓ 통계 버튼 발견: {stats_button_location}")
    logger.log_check("통계_버튼_찾기", True, f"위치: {stats_button_location}")

    screenshot = controller.screenshot()
    logger.save_screenshot(screenshot, "stats_button_found")

    print("\n[3단계] 통계 버튼 클릭...")
    print("1초 후 클릭합니다...")
    time.sleep(1)

    try:
        clicked = controller.click_template(stats_button_location, wait_after=2.0)
        if clicked:
            print("✓ 통계 버튼 클릭 성공")
            logger.log_check("통계_버튼_클릭", True, "클릭 완료")
            return True
        else:
            print("✗ 통계 버튼 클릭 실패")
            logger.log_check("통계_버튼_클릭", False, "클릭 실패")
            return False
    except Exception as e:
        print(f"✗ 클릭 중 오류: {e}")
        logger.log_check("통계_버튼_클릭", False, f"오류: {e}")
        return False


def verify_student_damage_entries(matcher, controller, logger):
    """학생별 데미지 항목 존재 여부 확인 (최대 6명)"""
    print("\n[4-1단계] 학생별 데미지 항목 확인...")
    time.sleep(1.0)  # 화면 안정화 대기

    # 학생 수 (최대 6명)
    max_students = 6
    verified_count = 0

    for i in range(1, max_students + 1):
        # 학생 아이콘 템플릿 경로
        student_icon = UI_DIR / f"student_icon_{i}.png"

        # 템플릿 파일이 없으면 스킵
        if not student_icon.exists():
            print(f"  ✗ 학생_{i} 아이콘 템플릿 없음 (스킵)")
            continue

        # 학생 아이콘 찾기
        icon_found = matcher.find_template(student_icon)

        if not icon_found:
            print(f"  ✗ 학생_{i} 아이콘 미발견 (데미지 기록 없음)")
            logger.log_check(f"학생_{i}_데미지_기록", False, "학생 아이콘 미발견")
            continue
        else:
            print(f"  ✓ 학생_{i} 데미지 기록 존재 (아이콘 확인)")
            logger.log_check(f"학생_{i}_데미지_기록", True, "학생 아이콘 발견")
            verified_count += 1
            continue

    print(f"\n  → 총 {verified_count}명의 학생 데미지 기록 확인")
    return verified_count > 0


def verify_damage_report(matcher, controller, logger):
    """4단계: 데미지 기록 창 확인"""
    print("\n[4단계] 데미지 기록 창 확인...")

    damage_report = UI_DIR / "damage_report.png"
    damage_report_appeared = matcher.wait_for_template(damage_report, timeout=10)

    if damage_report_appeared:
        print(f"✓ 데미지 기록 창 출현: {damage_report_appeared}")
        logger.log_check("데미지_기록_창_확인", True, f"위치: {damage_report_appeared}")

        screenshot = controller.screenshot()
        logger.save_screenshot(screenshot, "damage_report_found")

        # 학생별 데미지 항목 검증
        verify_student_damage_entries(matcher, controller, logger)

        return True
    else:
        print("✗ 데미지 기록 창이 10초 내에 나타나지 않음")
        logger.log_check("데미지_기록_창_확인", False, "타임아웃")

        screenshot = controller.screenshot()
        logger.save_screenshot(screenshot, "damage_report_timeout")
        return False


def click_damage_report_confirm(matcher, controller, logger):
    """5단계: 데미지 기록 창 확인 버튼 클릭"""
    print("\n[5단계] 데미지 기록 창 확인 버튼 클릭...")
    time.sleep(1.0)  # 화면 안정화 대기

    battle_log_confirm_button = BUTTONS_DIR / "battle_log_confirm_button.png"
    confirm_location = matcher.find_template(battle_log_confirm_button)

    if not confirm_location:
        print("✗ 확인 버튼을 찾을 수 없습니다")
        logger.log_check("데미지_기록_확인_버튼_클릭", False, "확인 버튼 미발견")
        return False

    print(f"✓ 확인 버튼 발견: {confirm_location}")
    print("1초 후 클릭합니다...")
    time.sleep(1)

    try:
        clicked = controller.click_template(confirm_location, wait_after=2.0)
        if clicked:
            print("✓ 확인 버튼 클릭 성공")
            logger.log_check("데미지_기록_확인_버튼_클릭", True, "클릭 완료")
            return True
        else:
            print("✗ 확인 버튼 클릭 실패")
            logger.log_check("데미지_기록_확인_버튼_클릭", False, "클릭 실패")
            return False
    except Exception as e:
        print(f"✗ 클릭 중 오류: {e}")
        logger.log_check("데미지_기록_확인_버튼_클릭", False, f"오류: {e}")
        return False


def click_victory_confirm(matcher, controller, logger):
    """6단계: 전투 결과 확인 버튼 클릭"""
    print("\n[6단계] 전투 결과 확인 버튼 클릭...")

    confirm_button = BUTTONS_DIR / "victory_confirm.png"
    confirm_location = matcher.find_template(confirm_button)

    if not confirm_location:
        print("✗ 확인 버튼을 찾을 수 없습니다")
        logger.log_check("전투_결과_확인_버튼_클릭", False, "확인 버튼 미발견")
        return False

    print(f"✓ 확인 버튼 발견: {confirm_location}")
    print("1초 후 클릭합니다...")
    time.sleep(1)

    try:
        clicked = controller.click_template(confirm_location, wait_after=2.0)
        if clicked:
            print("✓ 확인 버튼 클릭 성공")
            logger.log_check("전투_결과_확인_버튼_클릭", True, "클릭 완료")
            return True
        else:
            print("✗ 확인 버튼 클릭 실패")
            logger.log_check("전투_결과_확인_버튼_클릭", False, "클릭 실패")
            return False
    except Exception as e:
        print(f"✗ 클릭 중 오류: {e}")
        logger.log_check("전투_결과_확인_버튼_클릭", False, f"오류: {e}")
        return False


def verify_rank_reward(matcher, controller, logger):
    """7단계: 랭크 획득 창 확인"""
    print("\n[7단계] 랭크 획득 창 확인...")

    rank_reward_screen = UI_DIR / "rank_reward.png"
    rank_appeared = matcher.wait_for_template(rank_reward_screen, timeout=10)

    if rank_appeared:
        print(f"✓ 랭크 획득 창 출현: {rank_appeared}")
        logger.log_check("랭크_획득_창_확인", True, f"위치: {rank_appeared}")

        screenshot = controller.screenshot()
        logger.save_screenshot(screenshot, "rank_reward_found")
        return True
    else:
        print("✗ 랭크 획득 창이 10초 내에 나타나지 않음")
        logger.log_check("랭크_획득_창_확인", False, "타임아웃")

        screenshot = controller.screenshot()
        logger.save_screenshot(screenshot, "rank_reward_timeout")
        return False


def click_rank_reward_confirm(matcher, controller, logger):
    """8단계: 랭크 획득 창 확인 버튼 클릭"""
    print("\n[8단계] 랭크 획득 창 확인 버튼 클릭...")
    time.sleep(1.0)  # 화면 안정화 대기

    rank_reward_confirm_button = BUTTONS_DIR / "rank_reward_confirm_button.png"
    confirm_location = matcher.find_template(rank_reward_confirm_button)

    if not confirm_location:
        print("✗ 확인 버튼을 찾을 수 없습니다")
        logger.log_check("랭크_획득_확인_버튼_클릭", False, "확인 버튼 미발견")
        return False

    print(f"✓ 확인 버튼 발견: {confirm_location}")
    print("1초 후 클릭합니다...")
    time.sleep(1)

    try:
        clicked = controller.click_template(confirm_location, wait_after=3.0)
        if clicked:
            print("✓ 확인 버튼 클릭 성공")
            logger.log_check("랭크_획득_확인_버튼_클릭", True, "클릭 완료")
            return True
        else:
            print("✗ 확인 버튼 클릭 실패")
            logger.log_check("랭크_획득_확인_버튼_클릭", False, "클릭 실패")
            return False
    except Exception as e:
        print(f"✗ 클릭 중 오류: {e}")
        logger.log_check("랭크_획득_확인_버튼_클릭", False, f"오류: {e}")
        return False


def verify_stage_return(matcher, controller, logger):
    """9단계: 스테이지 화면 복귀 확인"""
    print("\n[9단계] 스테이지 화면 복귀 확인...")
    time.sleep(2.0)  # 화면 전환 대기

    stage_map = UI_DIR / "stage_map_2.png"
    stage_appeared = matcher.wait_for_template(stage_map, timeout=10)

    if stage_appeared:
        print(f"✓ 스테이지 화면 복귀 확인: {stage_appeared}")
        logger.log_check("스테이지_화면_복귀", True, f"위치: {stage_appeared}")

        screenshot = controller.screenshot()
        logger.save_screenshot(screenshot, "stage_map_returned")

        print("\n" + "="*60)
        print("✓ 테스트 성공!")
        print("="*60)
        print("\n전투 결과 확인 플로우가 정상적으로 작동합니다.")
        return True
    else:
        print("✗ 스테이지 화면이 10초 내에 나타나지 않음")
        logger.log_check("스테이지_화면_복귀", False, "타임아웃")

        screenshot = controller.screenshot()
        logger.save_screenshot(screenshot, "stage_map_timeout")

        print("\n" + "="*60)
        print("✗ 테스트 실패")
        print("="*60)
        return False


def test_battle_result_flow():
    """전투 결과 확인 플로우 테스트"""
    print("="*60)
    print("전투 결과 확인 플로우 테스트")
    print("="*60)

    # 템플릿 확인
    check_templates()

    # 초기화
    controller = GameController()
    logger = TestLogger("battle_result_test")

    print("\n" + "="*60)
    print("테스트 시작")
    print("="*60)
    print("\n게임이 Victory 화면에 있는지 확인하세요.")
    print("1초 후 테스트를 시작합니다...\n")
    time.sleep(1)

    # [1단계] Victory 화면 확인
    matcher = TemplateMatcher(confidence=0.5)
    if not verify_victory_screen(matcher, controller, logger):
        logger.finalize()
        return False

    # [2-3단계] 통계 버튼 찾기 및 클릭
    matcher = TemplateMatcher(confidence=0.7)
    if not click_battle_log_button(matcher, controller, logger):
        logger.finalize()
        return False

    # [4단계] 데미지 기록 창 확인
    if not verify_damage_report(matcher, controller, logger):
        logger.finalize()
        return False

    # [5단계] 데미지 기록 창 확인 버튼 클릭
    matcher = TemplateMatcher(confidence=0.5)
    if not click_damage_report_confirm(matcher, controller, logger):
        logger.finalize()
        return False

    # [6단계] 전투 결과 확인 버튼 클릭
    matcher = TemplateMatcher(confidence=0.7)
    if not click_victory_confirm(matcher, controller, logger):
        logger.finalize()
        return False

    # [7단계] 랭크 획득 창 확인
    if not verify_rank_reward(matcher, controller, logger):
        logger.finalize()
        return False

    # [8단계] 랭크 획득 창 확인 버튼 클릭
    if not click_rank_reward_confirm(matcher, controller, logger):
        logger.finalize()
        return False

    # [9단계] 스테이지 화면 복귀 확인
    result = verify_stage_return(matcher, controller, logger)

    result_file = logger.finalize()
    print(f"\n결과 파일: {result_file}")
    return result


def main():
    """메인 함수"""
    print("\n블루 아카이브 Normal 1-4 전투 결과 확인 테스트")
    print("\n테스트 범위: Victory → 통계 → 데미지 기록 → 랭크 획득 → 스테이지 복귀")
    print("\n준비사항:")
    print("1. 블루 아카이브 게임 실행")
    print("2. Normal 1-4 전투 승리 후 Victory 화면에서 대기")
    print("3. 게임 창이 화면에 보이도록 배치")
    print("\n⚠ 주의: 이 테스트는 Victory 화면에서 시작해야 합니다!")
    print("\n테스트를 시작합니다...\n")

    test_battle_result_flow()


if __name__ == "__main__":
    main()
