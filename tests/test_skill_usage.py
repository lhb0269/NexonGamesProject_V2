"""
스킬 사용 시스템 테스트

전투 화면에서 스킬 버튼 클릭 → 타겟 설정 → 코스트 소모 검증
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


def test_cost_recognizer_initialization():
    """코스트 인식 초기화 테스트"""
    print("=" * 70)
    print("[테스트 1] 템플릿 기반 코스트 인식 초기화")
    print("=" * 70)

    try:
        matcher = TemplateMatcher()
        controller = GameController()
        checker = SkillChecker(matcher, controller, enable_cost_check=True)

        if checker.enable_cost_check and checker.cost_recognizer:
            print("✓ CostRecognizer 초기화 성공")
            print(f"  - 코스트 인식 활성화: {checker.enable_cost_check}")
            print(f"  - 로드된 템플릿: {list(checker.cost_recognizer.templates.keys())}")
            return True, checker
        else:
            print("✗ CostRecognizer 초기화 실패")
            return False, None

    except Exception as e:
        print(f"✗ 예외 발생: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def test_read_skill_button_costs(checker: SkillChecker):
    """
    스킬 버튼 코스트 읽기 테스트 (3개 슬롯)

    게임을 전투 화면으로 진입시킨 후 실행하세요.
    """
    print("\n" + "=" * 70)
    print("[테스트 2] 스킬 버튼 코스트 읽기 (3개 슬롯)")
    print("=" * 70)
    print()
    print("준비사항:")
    print("1. 게임을 전투 화면으로 진입")
    print("2. 스킬 버튼 3개가 화면에 보이는 상태로 대기")
    print("3. 코스트 숫자가 명확하게 보이는 상태 유지")
    print()

    # 카운트다운
    for i in range(3, 0, -1):
        print(f"테스트 시작까지: {i}초...")
        time.sleep(1)

    print("\n스킬 코스트 읽기 시작...")

    try:
        # 한 번 캡처해서 3개 슬롯 모두 읽기
        screenshot = checker.controller.screenshot()

        results = []
        for slot_index in range(3):
            cost = checker.read_skill_cost_from_button(slot_index, screenshot)
            results.append((slot_index, cost))

            if cost is not None:
                print(f"✓ 슬롯 {slot_index + 1} 코스트: {cost}")
            else:
                print(f"✗ 슬롯 {slot_index + 1} 코스트 읽기 실패")

        # 성공 여부 판단
        success_count = sum(1 for _, cost in results if cost is not None)
        print()
        print(f"결과: {success_count}/3 슬롯 코스트 읽기 성공")

        return success_count > 0

    except Exception as e:
        print(f"✗ 예외 발생: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_single_skill_usage(checker: SkillChecker):
    """
    단일 스킬 사용 테스트

    게임을 전투 화면으로 진입시킨 후 실행하세요.
    슬롯 1의 스킬을 사용합니다.
    """
    print("\n" + "=" * 70)
    print("[테스트 3] 단일 스킬 사용 (슬롯 1)")
    print("=" * 70)
    print()
    print("준비사항:")
    print("1. 게임을 전투 화면으로 진입")
    print("2. 슬롯 1에 사용 가능한 스킬이 있는 상태")
    print("3. 현재 코스트가 스킬 코스트보다 높은 상태")
    print()

    # 카운트다운
    for i in range(1, 0, -1):
        print(f"테스트 시작까지: {i}초...")
        time.sleep(1)

    print("\n스킬 사용 시작...")

    try:
        # 슬롯 1 스킬 사용
        result = checker.use_skill_and_verify(
            slot_index=0,
            student_name="Test Student 1"
        )

        # 결과 출력
        print()
        print("=" * 70)
        print("스킬 사용 결과:")
        print("=" * 70)
        print(f"성공 여부: {result['success']}")
        print(f"학생 이름: {result['student_name']}")
        print(f"슬롯 인덱스: {result['slot_index'] + 1}")
        print(f"스킬 코스트: {result['skill_cost']}")
        print(f"사용 전 코스트: {result['cost_before']}")
        print(f"사용 후 코스트: {result['cost_after']}")
        print(f"소모된 코스트: {result['consumed']}")
        print(f"코스트 충분: {result['sufficient_cost']}")
        print(f"코스트 일치: {result['cost_matched']}")
        print(f"메시지: {result['message']}")
        print()

        return result['success']

    except Exception as e:
        print(f"✗ 예외 발생: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_skill_usage(checker: SkillChecker):
    """
    다중 스킬 사용 테스트

    게임을 전투 화면으로 진입시킨 후 실행하세요.
    슬롯 1, 2, 3의 스킬을 순차적으로 사용합니다.
    """
    print("\n" + "=" * 70)
    print("[테스트 4] 다중 스킬 사용 (슬롯 1, 2, 3)")
    print("=" * 70)
    print()
    print("준비사항:")
    print("1. 게임을 전투 화면으로 진입")
    print("2. 슬롯 1, 2, 3에 사용 가능한 스킬이 있는 상태")
    print("3. 현재 코스트가 충분히 높은 상태 (15+ 권장)")
    print()
    print("주의: 이 테스트는 실제로 3개의 스킬을 사용합니다!")
    print()

    user_input = input("계속 진행하시겠습니까? (y/n): ").strip().lower()
    if user_input != 'y':
        print("테스트 건너뜀")
        return False

    # 카운트다운
    for i in range(1, 0, -1):
        print(f"테스트 시작까지: {i}초...")
        time.sleep(1)

    print("\n다중 스킬 사용 시작...")

    try:
        results = []
        student_names = ["Student 1", "Student 2", "Student 3"]

        for slot_index in range(3):
            print()
            print(f"--- 슬롯 {slot_index + 1} 스킬 사용 ---")

            result = checker.use_skill_and_verify(
                slot_index=slot_index,
                student_name=student_names[slot_index]
            )

            results.append(result)

            print(f"결과: {result['message']}")

            # 다음 스킬까지 대기 (2초)
            if slot_index < 2:
                print("다음 스킬까지 2초 대기...")
                time.sleep(2)

        # 전체 결과 요약
        print()
        print("=" * 70)
        print("다중 스킬 사용 결과 요약")
        print("=" * 70)

        for i, result in enumerate(results):
            status = "✓ 성공" if result['success'] else "✗ 실패"
            print(f"{status}: 슬롯 {i + 1} - {result['student_name']}")
            print(f"  코스트: {result['skill_cost']}, "
                  f"사용 전: {result['cost_before']}, "
                  f"사용 후: {result['cost_after']}")

        success_count = sum(1 for r in results if r['success'])
        print()
        print(f"전체 결과: {success_count}/3 스킬 사용 성공")

        return success_count > 0

    except Exception as e:
        print(f"✗ 예외 발생: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_insufficient_cost_scenario(checker: SkillChecker):
    """
    코스트 부족 시나리오 테스트

    현재 코스트가 스킬 코스트보다 낮을 때 스킬이 발동되지 않는지 확인
    """
    print("\n" + "=" * 70)
    print("[테스트 5] 코스트 부족 시나리오")
    print("=" * 70)
    print()
    print("준비사항:")
    print("1. 게임을 전투 화면으로 진입")
    print("2. 현재 코스트가 낮은 상태 (1-3 정도)")
    print("3. 슬롯 1에 코스트가 높은 스킬 장착 (4+)")
    print()
    print("이 테스트는 스킬이 발동되지 않아야 정상입니다.")
    print()

    user_input = input("계속 진행하시겠습니까? (y/n): ").strip().lower()
    if user_input != 'y':
        print("테스트 건너뜀")
        return False

    # 카운트다운
    for i in range(1, 0, -1):
        print(f"테스트 시작까지: {i}초...")
        time.sleep(1)

    print("\n코스트 부족 시나리오 테스트 시작...")

    try:
        result = checker.use_skill_and_verify(
            slot_index=0,
            student_name="Test Student (Low Cost)"
        )

        print()
        print("=" * 70)
        print("코스트 부족 시나리오 결과:")
        print("=" * 70)
        print(f"스킬 발동: {result['success']}")
        print(f"코스트 충분: {result['sufficient_cost']}")
        print(f"메시지: {result['message']}")
        print()

        # 이 테스트는 success=False여야 정상
        if not result['success'] and not result['sufficient_cost']:
            print("✓ 코스트 부족 감지 정상 작동")
            return True
        else:
            print("✗ 코스트 부족임에도 스킬이 발동됨 (예상치 못한 동작)")
            return False

    except Exception as e:
        print(f"✗ 예외 발생: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """전체 테스트 실행"""
    print("=" * 70)
    print("스킬 사용 시스템 테스트 (템플릿 기반 코스트 인식)")
    print("=" * 70)
    print()
    print("주의사항:")
    print("- 코스트 템플릿 (cost_2~5.png)이 준비되어 있어야 합니다")
    print("- config/skill_settings.py의 좌표가 정확해야 합니다")
    print("- config/ocr_regions.py의 코스트 영역이 정확해야 합니다")
    print("- 게임 해상도: 2560x1440")
    print()

    # CostRecognizer 초기화
    success, checker = test_cost_recognizer_initialization()
    if not success:
        print("\n코스트 인식 초기화 실패. 테스트를 중단합니다.")
        return

    # 테스트 목록
    tests = [
        ("스킬 버튼 코스트 읽기", lambda: test_read_skill_button_costs(checker)),
        ("단일 스킬 사용", lambda: test_single_skill_usage(checker)),
        ("다중 스킬 사용", lambda: test_multiple_skill_usage(checker)),
        ("코스트 부족 시나리오", lambda: test_insufficient_cost_scenario(checker)),
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
