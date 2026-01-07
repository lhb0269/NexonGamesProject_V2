"""기본 모듈 테스트 스크립트

이 스크립트는 TemplateMatcher, GameController, TestLogger의 기본 기능을 테스트합니다.

사용법:
1. 테스트용 이미지 준비 (데스크톱 아이콘 등)
2. python tests/test_modules.py 실행
3. 프롬프트에 따라 진행
"""

import sys
import io
from pathlib import Path

# UTF-8 인코딩 강제 설정 (cp949 오류 방지)
# GUI 환경에서는 이미 stdout이 리다이렉션되어 있으므로 스킵
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.recognition.template_matcher import TemplateMatcher
from src.automation.game_controller import GameController
from src.logger.test_logger import TestLogger
import pyautogui
import time


def test_game_controller():
    """GameController 기본 기능 테스트"""
    print("\n" + "="*60)
    print("GameController 테스트 시작")
    print("="*60)

    controller = GameController()

    # 1. 화면 크기 확인
    width, height = controller.get_screen_size()
    print(f"✓ 화면 크기: {width}x{height}")

    # 2. 마우스 위치 확인
    x, y = controller.get_mouse_position()
    print(f"✓ 현재 마우스 위치: ({x}, {y})")

    # 3. 화면 캡처
    screenshot = controller.screenshot()
    print(f"✓ 화면 캡처 완료: {screenshot.size}")

    # 4. 안전한 클릭 테스트 (화면 중앙)
    center_x, center_y = width // 2, height // 2
    print(f"\n5초 후 화면 중앙({center_x}, {center_y})을 클릭합니다...")
    print("(취소하려면 마우스를 화면 좌측 상단 코너로 이동하세요)")

    for i in range(5, 0, -1):
        print(f"{i}...")
        time.sleep(1)

    try:
        controller.click(center_x, center_y)
        print("✓ 클릭 성공")
    except pyautogui.FailSafeException:
        print("✗ 사용자가 취소했습니다 (FailSafe)")

    print("\nGameController 테스트 완료!")
    return True


def test_template_matcher():
    """TemplateMatcher 기본 기능 테스트"""
    print("\n" + "="*60)
    print("TemplateMatcher 테스트 시작")
    print("="*60)

    matcher = TemplateMatcher(confidence=0.8, retry_count=2, timeout=5)

    print("\n테스트 방법:")
    print("1. 화면의 작은 영역(아이콘 등)을 스크린샷으로 찍어주세요")
    print("2. 이미지를 'test_template.png'로 저장해주세요")
    print("3. assets/templates/ui/ 폴더에 넣어주세요")

    template_path = project_root / "assets" / "templates" / "ui" / "test_template.png"

    if not template_path.exists():
        print(f"\n⚠ 테스트 템플릿이 없습니다: {template_path}")
        print("테스트를 건너뜁니다.")
        return False

    print(f"\n템플릿 파일 발견: {template_path}")
    print("5초 후 화면에서 템플릿을 찾습니다...")
    time.sleep(5)

    # 템플릿 찾기
    location = matcher.find_template(template_path)

    if location:
        print(f"✓ 템플릿 발견: {location}")

        # 중앙 좌표 확인
        center = matcher.find_template_center(template_path)
        print(f"✓ 중앙 좌표: {center}")

        # 존재 확인
        exists = matcher.template_exists(template_path)
        print(f"✓ 존재 확인: {exists}")

        # 클릭 테스트
        print(f"\n3초 후 템플릿 위치를 클릭합니다...")
        print("(취소하려면 마우스를 화면 좌측 상단 코너로 이동하세요)")
        for i in range(3, 0, -1):
            print(f"{i}...")
            time.sleep(1)

        try:
            controller = GameController()
            controller.click_template(location)
            print("✓ 템플릿 클릭 성공")
        except pyautogui.FailSafeException:
            print("✗ 사용자가 취소했습니다 (FailSafe)")
        except Exception as e:
            print(f"✗ 클릭 실패: {e}")

    else:
        print("✗ 템플릿을 찾지 못했습니다")
        print("  - 신뢰도(confidence)를 낮춰보세요")
        print("  - 화면에 해당 이미지가 있는지 확인하세요")

    print("\nTemplateMatcher 테스트 완료!")
    return location is not None


def test_logger():
    """TestLogger 기본 기능 테스트"""
    print("\n" + "="*60)
    print("TestLogger 테스트 시작")
    print("="*60)

    logger = TestLogger("module_test")

    # 검증 항목 기록
    logger.log_check(
        "테스트_항목_1",
        passed=True,
        message="정상 작동",
        details={"value": 100, "threshold": 80}
    )

    logger.log_check(
        "테스트_항목_2",
        passed=False,
        message="실패 시뮬레이션",
        details={"expected": "A", "actual": "B"}
    )

    # 에러 기록
    try:
        raise ValueError("테스트 에러")
    except Exception as e:
        logger.log_error("의도적인 에러 발생", e)

    # 스크린샷 저장
    screenshot = pyautogui.screenshot()
    logger.save_screenshot(screenshot, "test_screenshot")

    # 종료 및 결과 저장
    result_file = logger.finalize()

    print(f"\n✓ 테스트 결과 저장됨: {result_file}")
    print(f"✓ 로그 디렉토리: {logger.current_test_dir}")

    print("\nTestLogger 테스트 완료!")
    return True


def main():
    """메인 테스트 함수"""
    print("="*60)
    print("기본 모듈 테스트")
    print("="*60)
    print("\n이 스크립트는 다음을 테스트합니다:")
    print("1. GameController - 마우스/키보드 제어")
    print("2. TemplateMatcher - 이미지 인식")
    print("3. TestLogger - 결과 로깅")
    print("\n테스트를 시작합니다...\n")

    # 테스트 실행
    results = {}

    try:
        results["GameController"] = test_game_controller()
    except Exception as e:
        print(f"✗ GameController 테스트 실패: {e}")
        results["GameController"] = False

    try:
        results["TemplateMatcher"] = test_template_matcher()
    except Exception as e:
        print(f"✗ TemplateMatcher 테스트 실패: {e}")
        results["TemplateMatcher"] = False

    try:
        results["TestLogger"] = test_logger()
    except Exception as e:
        print(f"✗ TestLogger 테스트 실패: {e}")
        results["TestLogger"] = False

    # 최종 결과
    print("\n" + "="*60)
    print("테스트 결과 요약")
    print("="*60)
    for module, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status} - {module}")

    print("\n모든 테스트가 완료되었습니다!")


if __name__ == "__main__":
    main()
