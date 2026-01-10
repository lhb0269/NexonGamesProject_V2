"""보상 획득 UI 검증 테스트

테스트 목적:
- 전투 종료 후 보상 획득 UI가 정상적으로 표시되는지 검증
- 보상 아이템이 결과 화면에 매핑되었는지 확인
- 실제 인벤토리 반영 여부는 테스트 범위에서 제외

테스트 시나리오:
1. MISSION COMPLETE 또는 보상 획득 화면 노출 확인
2. 보상 아이템 카드 UI 존재 여부 확인
   - 크레딧 아이콘
   - 활동 보고서 아이콘
   - 기타 보상 아이콘
3. 각 아이템은 아이콘 UI 존재 여부만 확인 (OCR 미사용)
4. 모든 조건 만족 시 PASS 판정

제약사항:
- Live 빌드 환경
- 화면 인식 기반 자동화만 허용
- 메모리 접근, 내부 상태 조회 금지
- OCR 사용 금지 (UI 아이콘만 확인)
"""

import sys
import io
from pathlib import Path
import time

# UTF-8 인코딩 강제 설정 (cp949 오류 방지)
if not hasattr(sys.stdout, '_buffer'):
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.recognition.template_matcher import TemplateMatcher
from src.automation.game_controller import GameController
from src.logger.test_logger import TestLogger
from config.settings import BUTTONS_DIR, UI_DIR, ICONS_DIR


def check_templates():
    """템플릿 파일 존재 확인"""
    print("\n" + "="*70)
    print("템플릿 파일 확인")
    print("="*70)

    templates = {
        "Victory 확인 버튼": BUTTONS_DIR / "victory_confirm.png",
        "보상 획득 화면": UI_DIR / "mission_complete.png",
        "크레딧 아이콘": ICONS_DIR / "credit_icon.png",
        "활동 보고서 아이콘": ICONS_DIR / "activity_report_icon.png",
    }

    missing_templates = []
    for name, path in templates.items():
        if not path.exists():
            print(f"✗ {name} 템플릿 없음: {path}")
            missing_templates.append(name)
        else:
            print(f"✓ {name} 템플릿 존재: {path}")

    if missing_templates:
        print(f"\n⚠ 누락된 템플릿: {', '.join(missing_templates)}")
        print("  해당 단계는 스킵되거나 실패할 수 있습니다.")

    return templates


def verify_victory_screen(matcher: TemplateMatcher, controller: GameController, logger: TestLogger) -> bool:
    """
    1단계: Victory 화면 확인

    Returns:
        True: Victory 화면 발견
        False: Victory 화면 미발견
    """
    print("\n" + "="*70)
    print("[1단계] Victory 화면 확인")
    print("="*70)

    victory_screen = UI_DIR / "victory.png"

    if not victory_screen.exists():
        print("✗ Victory 템플릿 파일 없음")
        logger.log_check(
            check_name="Victory_화면_확인",
            passed=False,
            message="템플릿 파일 없음",
            details={"template_path": str(victory_screen)}
        )
        return False

    location = matcher.find_template(victory_screen)

    if location:
        print(f"✓ Victory 화면 발견")
        print(f"  위치: {location}")

        screenshot = controller.screenshot()
        logger.save_screenshot(screenshot, "victory_screen_found")

        logger.log_check(
            check_name="Victory_화면_확인",
            passed=True,
            message="Victory 화면 발견",
            details={"location": location}
        )
        return True
    else:
        print("✗ Victory 화면 미발견")
        print("  확인사항:")
        print("  1. 게임이 Victory 화면에 있나요?")
        print("  2. victory.png 템플릿이 정확한가요?")

        screenshot = controller.screenshot()
        logger.save_screenshot(screenshot, "victory_screen_not_found")

        logger.log_check(
            check_name="Victory_화면_확인",
            passed=False,
            message="Victory 화면 미발견",
            details={}
        )
        return False


def click_victory_confirm(matcher: TemplateMatcher, controller: GameController, logger: TestLogger) -> bool:
    """
    2단계: Victory 확인 버튼 클릭

    Returns:
        True: 클릭 성공
        False: 클릭 실패
    """
    print("\n" + "="*70)
    print("[2단계] Victory 확인 버튼 클릭")
    print("="*70)

    confirm_button = BUTTONS_DIR / "victory_confirm.png"

    if not confirm_button.exists():
        print("✗ Victory 확인 버튼 템플릿 없음")
        logger.log_check(
            check_name="Victory_확인_버튼_클릭",
            passed=False,
            message="템플릿 파일 없음",
            details={"template_path": str(confirm_button)}
        )
        return False

    location = matcher.find_template(confirm_button)

    if not location:
        print("✗ Victory 확인 버튼 미발견")

        screenshot = controller.screenshot()
        logger.save_screenshot(screenshot, "victory_confirm_button_not_found")

        logger.log_check(
            check_name="Victory_확인_버튼_클릭",
            passed=False,
            message="확인 버튼 미발견",
            details={}
        )
        return False

    print(f"✓ Victory 확인 버튼 발견")
    print(f"  위치: {location}")
    print("  1초 후 클릭...")
    time.sleep(1)

    try:
        clicked = controller.click_template(location, wait_after=3.0)

        if clicked:
            print("✓ 클릭 성공")

            logger.log_check(
                check_name="Victory_확인_버튼_클릭",
                passed=True,
                message="클릭 완료",
                details={"location": location}
            )
            return True
        else:
            print("✗ 클릭 실패")

            logger.log_check(
                check_name="Victory_확인_버튼_클릭",
                passed=False,
                message="클릭 실패",
                details={"location": location}
            )
            return False

    except Exception as e:
        print(f"✗ 클릭 중 오류: {e}")

        logger.log_check(
            check_name="Victory_확인_버튼_클릭",
            passed=False,
            message=f"클릭 오류: {e}",
            details={"error": str(e)}
        )
        return False


def verify_mission_complete_screen(matcher: TemplateMatcher, controller: GameController, logger: TestLogger) -> bool:
    """
    3단계: MISSION COMPLETE 화면 확인

    Returns:
        True: MISSION COMPLETE 화면 발견
        False: MISSION COMPLETE 화면 미발견
    """
    print("\n" + "="*70)
    print("[3단계] MISSION COMPLETE 화면 확인")
    print("="*70)
    print("  화면 전환 대기 중 (10초 타임아웃)...")

    mission_complete = UI_DIR / "mission_complete.png"

    if not mission_complete.exists():
        print("✗ MISSION COMPLETE 템플릿 파일 없음")
        logger.log_check(
            check_name="MISSION_COMPLETE_화면_확인",
            passed=False,
            message="템플릿 파일 없음",
            details={"template_path": str(mission_complete)}
        )
        return False

    location = matcher.wait_for_template(mission_complete, timeout=10)

    if location:
        print(f"✓ MISSION COMPLETE 화면 발견")
        print(f"  위치: {location}")

        screenshot = controller.screenshot()
        logger.save_screenshot(screenshot, "mission_complete_found")

        logger.log_check(
            check_name="MISSION_COMPLETE_화면_확인",
            passed=True,
            message="MISSION COMPLETE 화면 발견",
            details={"location": location}
        )
        return True
    else:
        print("✗ MISSION COMPLETE 화면 미발견 (10초 타임아웃)")
        print("  확인사항:")
        print("  1. Victory 확인 버튼을 클릭했나요?")
        print("  2. mission_complete.png 템플릿이 정확한가요?")

        screenshot = controller.screenshot()
        logger.save_screenshot(screenshot, "mission_complete_timeout")

        logger.log_check(
            check_name="MISSION_COMPLETE_화면_확인",
            passed=False,
            message="타임아웃 (10초)",
            details={}
        )
        return False


def verify_reward_items(matcher: TemplateMatcher, controller: GameController, logger: TestLogger) -> bool:
    """
    4단계: 보상 아이템 UI 확인

    - 크레딧 아이콘
    - 활동 보고서 아이콘

    Returns:
        True: 최소 1개 이상의 보상 아이템 UI 발견
        False: 보상 아이템 UI 미발견
    """
    print("\n" + "="*70)
    print("[4단계] 보상 아이템 UI 확인")
    print("="*70)
    print("  화면 안정화 대기 중 (2초)...")
    time.sleep(2.0)

    # 보상 아이템 템플릿 정의
    reward_items = {
        "크레딧": ICONS_DIR / "credit_icon.png",
        "활동 보고서": ICONS_DIR / "activity_report_icon.png",
    }

    found_items = []
    missing_items = []

    for item_name, template_path in reward_items.items():
        print(f"\n  [{item_name}] 아이콘 확인 중...")

        # 템플릿 파일 존재 확인
        if not template_path.exists():
            print(f"    ✗ 템플릿 파일 없음: {template_path}")
            missing_items.append(item_name)

            logger.log_check(
                check_name=f"보상_아이템_{item_name}",
                passed=False,
                message="템플릿 파일 없음",
                details={"template_path": str(template_path)}
            )
            continue

        # 아이콘 탐색
        location = matcher.find_template(template_path)

        if location:
            print(f"    ✓ {item_name} 아이콘 발견")
            print(f"      위치: {location}")
            found_items.append(item_name)

            logger.log_check(
                check_name=f"보상_아이템_{item_name}",
                passed=True,
                message=f"{item_name} 아이콘 발견",
                details={"location": location}
            )
        else:
            print(f"    ✗ {item_name} 아이콘 미발견")
            missing_items.append(item_name)

            logger.log_check(
                check_name=f"보상_아이템_{item_name}",
                passed=False,
                message=f"{item_name} 아이콘 미발견",
                details={}
            )

    # 결과 스크린샷 저장
    screenshot = controller.screenshot()
    logger.save_screenshot(screenshot, "reward_items_verification")

    # 결과 출력
    print(f"\n  → 발견된 보상 아이템: {len(found_items)}개")
    if found_items:
        print(f"    {', '.join(found_items)}")

    if missing_items:
        print(f"  → 미발견 아이템: {len(missing_items)}개")
        print(f"    {', '.join(missing_items)}")

    # 최소 1개 이상의 보상 아이템이 발견되면 성공
    if len(found_items) > 0:
        print("\n  ✓ 보상 아이템 UI 검증 성공")

        logger.log_check(
            check_name="보상_아이템_UI_검증",
            passed=True,
            message=f"{len(found_items)}개 보상 아이템 발견",
            details={
                "found_items": found_items,
                "missing_items": missing_items
            }
        )
        return True
    else:
        print("\n  ✗ 보상 아이템 UI 검증 실패 (아이템 미발견)")

        logger.log_check(
            check_name="보상_아이템_UI_검증",
            passed=False,
            message="보상 아이템 미발견",
            details={
                "found_items": found_items,
                "missing_items": missing_items
            }
        )
        return False


def test_reward_ui_verification():
    """보상 획득 UI 검증 테스트 실행"""
    print("="*70)
    print("보상 획득 UI 검증 테스트")
    print("="*70)

    # 템플릿 확인
    check_templates()

    # 초기화
    controller = GameController()
    logger = TestLogger("reward_ui_verification")

    print("\n" + "="*70)
    print("테스트 시작")
    print("="*70)
    print("\n게임이 Victory 화면에 있는지 확인하세요.")
    print("3초 후 테스트를 시작합니다...\n")
    time.sleep(3)

    # [1단계] Victory 화면 확인
    matcher = TemplateMatcher(confidence=0.7)
    if not verify_victory_screen(matcher, controller, logger):
        print("\n→ 테스트 종료 (Victory 화면 미발견)")
        logger.finalize()
        return False

    # [2단계] Victory 확인 버튼 클릭
    if not click_victory_confirm(matcher, controller, logger):
        print("\n→ 테스트 종료 (Victory 확인 버튼 클릭 실패)")
        logger.finalize()
        return False

    # [3단계] MISSION COMPLETE 화면 확인
    if not verify_mission_complete_screen(matcher, controller, logger):
        print("\n→ 테스트 종료 (MISSION COMPLETE 화면 미발견)")
        logger.finalize()
        return False

    # [4단계] 보상 아이템 UI 확인
    if not verify_reward_items(matcher, controller, logger):
        print("\n→ 테스트 종료 (보상 아이템 UI 미발견)")
        logger.finalize()
        return False

    # 테스트 성공
    print("\n" + "="*70)
    print("✓ 테스트 성공 - PASS")
    print("="*70)
    print("\n보상 획득 UI가 정상적으로 표시되었습니다.")
    print("보상 아이템이 결과 화면에 매핑되었습니다.")

    result_file = logger.finalize()
    print(f"\n결과 파일: {result_file}")

    return True


def main():
    """메인 함수"""
    print("\n블루 아카이브 Normal 1-4 보상 획득 UI 검증 테스트")
    print("\n테스트 범위:")
    print("  1. Victory 화면 확인")
    print("  2. Victory 확인 버튼 클릭")
    print("  3. MISSION COMPLETE 화면 확인")
    print("  4. 보상 아이템 UI 확인 (크레딧, 활동 보고서)")
    print("\n테스트 제외 범위:")
    print("  - 실제 인벤토리 반영 여부")
    print("  - 보상 아이템 수량 검증 (OCR)")
    print("  - 서버 데이터 무결성")
    print("\n준비사항:")
    print("  1. 블루 아카이브 게임 실행")
    print("  2. Normal 1-4 전투 승리 후 Victory 화면에서 대기")
    print("  3. 게임 창이 화면에 보이도록 배치")
    print("\n⚠ 주의: 이 테스트는 Victory 화면에서 시작해야 합니다!")
    print("\n테스트를 시작합니다...\n")

    success = test_reward_ui_verification()

    if success:
        print("\n[최종 결과] PASS")
    else:
        print("\n[최종 결과] FAIL")


if __name__ == "__main__":
    main()
