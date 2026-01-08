"""게이지 면적 기반 코스트 검증 테스트

숫자 읽기 대신 '상태 변화'로 코스트 소모를 증명하는 방식 테스트

검증 방법:
- Before: 게이지 픽셀 수 = A
- Action: 스킬 사용
- After: 게이지 픽셀 수 = B
- if A > B: 코스트 소모 확인 ✓

장점:
- 많은 픽셀 → 노이즈 평균화
- 프레임 흔들림 영향 적음
- OCR/템플릿 매칭 불필요
- QA 자동화 베스트 프랙티스
"""

import sys
import io
from pathlib import Path

# UTF-8 인코딩 강제 설정
if not hasattr(sys.stdout, '_buffer'):
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.recognition.template_matcher import TemplateMatcher
from src.recognition.cost_gauge_analyzer import CostGaugeAnalyzer
from src.automation.game_controller import GameController
from src.verification.skill_checker import SkillChecker
from src.logger.test_logger import TestLogger
from config.ocr_regions import BATTLE_COST_GAUGE_REGION
import time


def test_gauge_analyzer_basic():
    """게이지 분석기 기본 테스트"""
    print("=" * 60)
    print("게이지 분석기 기본 테스트")
    print("=" * 60)

    try:
        analyzer = CostGaugeAnalyzer()
        print("✓ CostGaugeAnalyzer 초기화 성공")
        print(f"  게이지 HSV 범위: {analyzer.lower_gauge} ~ {analyzer.upper_gauge}")
        return True
    except Exception as e:
        print(f"✗ CostGaugeAnalyzer 초기화 실패: {e}")
        return False


def test_gauge_pixel_counting():
    """게이지 픽셀 카운팅 테스트"""
    print("\n" + "=" * 60)
    print("게이지 픽셀 카운팅 테스트")
    print("=" * 60)

    controller = GameController()
    analyzer = CostGaugeAnalyzer()
    logger = TestLogger("gauge_pixel_count_test")

    print("\n게임 화면에서 전투 중이어야 합니다.")
    print("코스트 게이지가 보이는 상태에서 테스트합니다.")
    print("5초 후 현재 코스트 게이지를 캡처합니다...")

    for i in range(5, 0, -1):
        print(f"{i}초 남음...")
        time.sleep(1)

    print("\n[1단계] 현재 게이지 픽셀 카운팅...")

    try:
        # 스크린샷 캡처
        screenshot = controller.screenshot()
        logger.save_screenshot(screenshot, "gauge_screenshot")

        # NumPy 배열로 변환
        import numpy as np
        screenshot_array = np.array(screenshot)

        # 게이지 픽셀 카운트
        pixel_count = analyzer.count_gauge_pixels(
            screenshot_array,
            BATTLE_COST_GAUGE_REGION
        )

        print(f"✓ 게이지 픽셀 수: {pixel_count}px")
        print(f"  영역: {BATTLE_COST_GAUGE_REGION}")

        logger.log_check(
            "게이지_픽셀_카운팅",
            True,
            f"픽셀 수: {pixel_count}px"
        )

        result_file = logger.finalize()
        print(f"\n결과 파일: {result_file}")

        return True

    except Exception as e:
        print(f"✗ 픽셀 카운팅 실패: {e}")
        import traceback
        traceback.print_exc()

        logger.log_check("게이지_픽셀_카운팅", False, f"오류: {e}")
        logger.finalize()

        return False


def test_skill_usage_with_gauge_verification():
    """스킬 사용 + 게이지 면적 검증 통합 테스트"""
    print("\n" + "=" * 60)
    print("스킬 사용 + 게이지 면적 검증 통합 테스트")
    print("=" * 60)

    matcher = TemplateMatcher(confidence=0.8)
    controller = GameController()

    # 게이지 검증 활성화
    skill_checker = SkillChecker(
        matcher,
        controller,
        enable_cost_check=True,
        use_gauge_verification=True  # 게이지 검증 사용
    )

    logger = TestLogger("skill_gauge_verification_test")

    print("\n게임 화면에서 전투 중이어야 합니다.")
    print("코스트가 충분한 상태에서 스킬을 사용할 수 있어야 합니다.")
    print("\n테스트할 스킬 슬롯: 1번 (좌측)")
    print("10초 후 스킬을 사용합니다...\n")

    for i in range(10, 0, -1):
        print(f"{i}초 남음...")
        time.sleep(1)

    print("\n[테스트 시작]")

    try:
        # Before 스크린샷
        screenshot_before = controller.screenshot()
        logger.save_screenshot(screenshot_before, "before_skill_use")

        # 스킬 사용 + 게이지 검증
        result = skill_checker.use_skill_and_verify_by_gauge(
            slot_index=0,  # 슬롯 1
            student_name="테스트_학생1",
            min_decrease_threshold=50  # 최소 50px 감소
        )

        # After 스크린샷
        screenshot_after = controller.screenshot()
        logger.save_screenshot(screenshot_after, "after_skill_use")

        # 결과 출력
        print("\n[검증 결과]")
        print(f"  성공 여부: {result['success']}")
        print(f"  Before 픽셀: {result['before_pixels']}px")
        print(f"  After 픽셀: {result['after_pixels']}px")
        print(f"  감소 픽셀: {result['decreased_pixels']}px")
        print(f"  감소 비율: {result['decreased_ratio']:.1%}")
        print(f"  메시지: {result['message']}")

        if result["success"]:
            print("\n✓ 스킬 사용 및 코스트 소모 확인 성공!")
            logger.log_check(
                "스킬_사용_게이지_검증",
                True,
                f"감소: {result['decreased_pixels']}px ({result['decreased_ratio']:.1%})"
            )
        else:
            print("\n✗ 검증 실패")
            logger.log_check(
                "스킬_사용_게이지_검증",
                False,
                result["message"]
            )

        result_file = logger.finalize()
        print(f"\n결과 파일: {result_file}")

        return result["success"]

    except Exception as e:
        print(f"\n✗ 테스트 중 오류: {e}")
        import traceback
        traceback.print_exc()

        logger.log_check("스킬_사용_게이지_검증", False, f"오류: {e}")
        logger.finalize()

        return False


def test_multiple_skill_usage():
    """다중 스킬 사용 테스트 (3개 연속)"""
    print("\n" + "=" * 60)
    print("다중 스킬 사용 테스트 (게이지 검증)")
    print("=" * 60)

    matcher = TemplateMatcher(confidence=0.8)
    controller = GameController()

    skill_checker = SkillChecker(
        matcher,
        controller,
        enable_cost_check=True,
        use_gauge_verification=True
    )

    logger = TestLogger("multiple_skill_gauge_test")

    print("\n게임 화면에서 전투 중이어야 합니다.")
    print("코스트가 충분한 상태에서 3개 스킬을 연속으로 사용합니다.")
    print("10초 후 시작...\n")

    for i in range(10, 0, -1):
        print(f"{i}초 남음...")
        time.sleep(1)

    print("\n[테스트 시작]")

    students = ["학생1", "학생2", "학생3"]
    results = []

    for slot_idx, student_name in enumerate(students):
        print(f"\n{'=' * 40}")
        print(f"슬롯 {slot_idx + 1}: {student_name}")
        print('=' * 40)

        try:
            result = skill_checker.use_skill_and_verify_by_gauge(
                slot_index=slot_idx,
                student_name=student_name,
                min_decrease_threshold=50
            )

            results.append(result)

            print(f"  결과: {'✓ 성공' if result['success'] else '✗ 실패'}")
            print(f"  감소: {result['decreased_pixels']}px ({result['decreased_ratio']:.1%})")
            print(f"  메시지: {result['message']}")

            logger.log_check(
                f"스킬_{slot_idx + 1}_{student_name}",
                result["success"],
                f"감소: {result['decreased_pixels']}px"
            )

            # 다음 스킬까지 대기
            if slot_idx < 2:
                print("\n2초 대기...")
                time.sleep(2)

        except Exception as e:
            print(f"  ✗ 오류: {e}")
            logger.log_check(f"스킬_{slot_idx + 1}_{student_name}", False, f"오류: {e}")
            results.append({"success": False})

    # 전체 결과
    print("\n" + "=" * 60)
    print("전체 결과")
    print("=" * 60)

    success_count = sum(1 for r in results if r.get("success", False))
    total_count = len(results)

    print(f"성공: {success_count}/{total_count}")

    for idx, result in enumerate(results):
        status = "✓" if result.get("success", False) else "✗"
        print(f"  슬롯 {idx + 1}: {status} {students[idx]}")

    result_file = logger.finalize()
    print(f"\n결과 파일: {result_file}")

    return success_count == total_count


def main():
    """메인 함수"""
    print("\n게이지 면적 기반 코스트 검증 테스트")
    print("\n테스트 방법:")
    print("- OCR/템플릿 매칭 대신 게이지 픽셀 면적 변화로 코스트 소모 검증")
    print("- Before/After 비교로 '상태 변화' 증명")
    print("\n장점:")
    print("- 많은 픽셀 → 노이즈 평균화")
    print("- 프레임 흔들림 영향 적음")
    print("- QA 자동화 베스트 프랙티스")

    print("\n" + "=" * 60)
    print("테스트 메뉴")
    print("=" * 60)
    print("1. 게이지 분석기 기본 테스트")
    print("2. 게이지 픽셀 카운팅 테스트")
    print("3. 스킬 사용 + 게이지 검증 (1개)")
    print("4. 다중 스킬 사용 + 게이지 검증 (3개)")
    print("0. 전체 테스트 실행")

    choice = input("\n선택 (0-4): ").strip()

    if choice == "1":
        test_gauge_analyzer_basic()
    elif choice == "2":
        test_gauge_pixel_counting()
    elif choice == "3":
        test_skill_usage_with_gauge_verification()
    elif choice == "4":
        test_multiple_skill_usage()
    elif choice == "0":
        print("\n전체 테스트 실행")
        test_gauge_analyzer_basic()
        test_gauge_pixel_counting()
        test_skill_usage_with_gauge_verification()
        test_multiple_skill_usage()
    else:
        print("잘못된 선택입니다.")


if __name__ == "__main__":
    main()
