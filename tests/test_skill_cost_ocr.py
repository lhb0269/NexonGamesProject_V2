"""
스킬 코스트 OCR 검증 테스트

실제 전투 화면에서 코스트를 읽고 스킬 사용 전후 비교를 테스트합니다.
"""

import sys
from pathlib import Path
import time

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.recognition.template_matcher import TemplateMatcher
from src.automation.game_controller import GameController
from src.verification.skill_checker import SkillChecker
from src.logger.test_logger import TestLogger


def test_ocr_initialization():
    """OCR 초기화 테스트"""
    print("=" * 70)
    print("[테스트 1] OCR 초기화")
    print("=" * 70)

    try:
        matcher = TemplateMatcher()
        controller = GameController()
        checker = SkillChecker(matcher, controller, enable_ocr=True)

        if checker.enable_ocr and checker.ocr_reader:
            print("✓ OCR 초기화 성공")
            print(f"  - OCR 활성화: {checker.enable_ocr}")
            return True
        else:
            print("✗ OCR 초기화 실패")
            return False

    except Exception as e:
        print(f"✗ 예외 발생: {e}")
        return False


def test_cost_reading_manual():
    """
    수동 코스트 읽기 테스트

    게임을 전투 화면으로 진입시킨 후 실행하세요.
    """
    print("\n" + "=" * 70)
    print("[테스트 2] 코스트 읽기 (수동)")
    print("=" * 70)
    print()
    print("준비사항:")
    print("1. 게임을 전투 화면으로 진입")
    print("2. 코스트 UI가 화면에 보이는 상태로 대기")
    print()

    # 카운트다운
    for i in range(3, 0, -1):
        print(f"테스트 시작까지: {i}초...")
        time.sleep(1)

    print("\n코스트 읽기 시작...")

    try:
        matcher = TemplateMatcher()
        controller = GameController()
        checker = SkillChecker(matcher, controller, enable_ocr=True)

        if not checker.enable_ocr:
            print("✗ OCR이 활성화되지 않았습니다")
            return False

        # 현재 화면 캡처 및 코스트 읽기
        screenshot = controller.screenshot()
        cost = checker.read_current_cost(screenshot)

        if cost is not None:
            print(f"✓ 코스트 읽기 성공: {cost}")
            return True
        else:
            print("✗ 코스트 읽기 실패")
            print("  → OCR 영역 좌표(config/ocr_regions.py)를 확인하세요")
            return False

    except Exception as e:
        print(f"✗ 예외 발생: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cost_verification_demo():
    """
    코스트 검증 데모 (시뮬레이션)

    실제 스킬 사용 없이 현재 코스트만 읽어서 검증 로직 테스트
    """
    print("\n" + "=" * 70)
    print("[테스트 3] 코스트 검증 로직 (시뮬레이션)")
    print("=" * 70)
    print()

    # 카운트다운
    for i in range(2, 0, -1):
        print(f"테스트 시작까지: {i}초...")
        time.sleep(1)

    try:
        matcher = TemplateMatcher()
        controller = GameController()
        checker = SkillChecker(matcher, controller, enable_ocr=True)

        if not checker.enable_ocr:
            print("✗ OCR이 활성화되지 않았습니다")
            return False

        # 현재 코스트 읽기
        current_cost = checker.read_current_cost()

        if current_cost is None:
            print("✗ 코스트 읽기 실패")
            return False

        print(f"현재 코스트: {current_cost}")
        print()

        # 가상의 스킬 코스트로 검증 시뮬레이션
        test_skill_costs = [2, 3, 5, 8]

        for skill_cost in test_skill_costs:
            if current_cost >= skill_cost:
                print(f"✓ 스킬 코스트 {skill_cost}: 사용 가능 (현재: {current_cost})")
            else:
                print(f"✗ 스킬 코스트 {skill_cost}: 코스트 부족 (현재: {current_cost})")

        return True

    except Exception as e:
        print(f"✗ 예외 발생: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """전체 테스트 실행"""
    print("=" * 70)
    print("스킬 코스트 OCR 검증 테스트")
    print("=" * 70)
    print()
    print("주의사항:")
    print("- Tesseract OCR이 설치되어 있어야 합니다")
    print("- 테스트 2, 3은 게임이 전투 화면에 있어야 합니다")
    print("- config/ocr_regions.py의 좌표가 정확해야 합니다")
    print()

    tests = [
        ("OCR 초기화", test_ocr_initialization),
        ("코스트 읽기 (수동)", test_cost_reading_manual),
        ("코스트 검증 로직", test_cost_verification_demo),
    ]

    results = []
    for name, test_func in tests:
        result = test_func()
        results.append((name, result))

        if not result:
            print()
            print(f"⚠️  '{name}' 테스트 실패. 다음 테스트를 계속하시겠습니까? (y/n)")
            user_input = input().strip().lower()
            if user_input != 'y':
                print("테스트 중단")
                break

    # 결과 요약
    print("\n" + "=" * 70)
    print("테스트 결과 요약")
    print("=" * 70)

    for name, result in results:
        status = "✓ 통과" if result else "✗ 실패"
        print(f"{status}: {name}")

    passed = sum(1 for _, result in results if result)
    total = len(results)
    print()
    print(f"전체 결과: {passed}/{total} 통과")
    print("=" * 70)


if __name__ == "__main__":
    main()
