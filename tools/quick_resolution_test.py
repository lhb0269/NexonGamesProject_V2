"""빠른 해상도 호환성 테스트

1920x1080 환경에서 1920x1080 템플릿이 잘 인식되는지만 확인
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pyautogui
from config.settings import TEMPLATES_DIR


def quick_test():
    """빠른 테스트"""

    print("\n" + "="*60)
    print("해상도 호환성 빠른 테스트")
    print("="*60)

    # 현재 화면 해상도
    screen_width, screen_height = pyautogui.size()
    current_res = f"{screen_width}x{screen_height}"

    print(f"\n✓ 현재 화면 해상도: {current_res}")

    # 1920x1080 템플릿 경로
    template_1080 = TEMPLATES_DIR / "1920x1080" / "buttons" / "deploy_button.png"

    if not template_1080.exists():
        print(f"\n✗ 템플릿 파일이 없습니다: {template_1080}")
        print("먼저 템플릿을 준비해주세요.")
        return

    print(f"\n✓ 템플릿 파일 존재: {template_1080}")
    print("\n" + "="*60)
    print("준비사항:")
    print("  1. 블루 아카이브 게임 실행")
    print("  2. '출격' 버튼이 보이는 화면으로 이동")
    print("  3. 게임 창이 화면에 보이도록 배치")
    print("="*60)
    print("\n10초 후 테스트를 시작합니다...\n")

    import time
    for i in range(5, 0, -1):
        print(f"{i}초 남음...")
        time.sleep(1)

    print("\n템플릿 인식 테스트 중...")

    try:
        # 신뢰도 0.8로 시도
        location = pyautogui.locateOnScreen(str(template_1080), confidence=0.8)

        if location:
            print(f"\n✓✓✓ 성공! ✓✓✓")
            print(f"위치: {location}")
            print(f"\n결론: 1920x1080 템플릿이 {current_res} 환경에서 작동합니다!")
        else:
            print(f"\n✗ 신뢰도 0.8에서 인식 실패")
            print("신뢰도를 낮춰서 재시도 중...")

            location = pyautogui.locateOnScreen(str(template_1080), confidence=0.6)

            if location:
                print(f"\n⚠ 신뢰도 0.6에서 인식됨")
                print(f"위치: {location}")
                print(f"\n결론: 인식은 되지만 신뢰도가 낮습니다. 템플릿 재캡처 권장.")
            else:
                print(f"\n✗✗✗ 실패 ✗✗✗")
                print(f"신뢰도 0.6에서도 인식 실패")
                print(f"\n가능한 원인:")
                print(f"  1. 게임 화면에 '출격' 버튼이 안 보임")
                print(f"  2. 템플릿 이미지가 정확하지 않음")
                print(f"  3. 게임 UI 크기가 다름")

    except Exception as e:
        print(f"\n✗ 오류 발생: {e}")


if __name__ == "__main__":
    quick_test()
