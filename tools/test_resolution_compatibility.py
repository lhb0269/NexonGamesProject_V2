"""해상도 호환성 테스트

다른 해상도의 템플릿으로 현재 해상도에서 인식이 되는지 테스트합니다.
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pyautogui
from config.settings import TEMPLATES_DIR


def test_template_compatibility():
    """템플릿 호환성 테스트"""

    print("\n" + "="*60)
    print("해상도별 템플릿 호환성 테스트")
    print("="*60)

    # 현재 화면 해상도
    screen_width, screen_height = pyautogui.size()
    current_res = f"{screen_width}x{screen_height}"

    print(f"\n현재 화면 해상도: {current_res}")
    print()

    # 테스트할 템플릿 (간단한 것 하나만)
    test_templates = {
        "1920x1080": TEMPLATES_DIR / "1920x1080" / "buttons" / "deploy_button.png",
        "2560x1440": TEMPLATES_DIR / "2560x1440" / "buttons" / "deploy_button.png",
    }

    print("테스트 시작:")
    print("게임을 실행하고 '출격' 버튼이 보이는 화면에서 대기하세요.")
    print("10초 후 테스트를 시작합니다...\n")

    import time
    for i in range(10, 0, -1):
        print(f"{i}초 남음...")
        time.sleep(1)

    print("\n" + "="*60)
    print("템플릿 인식 테스트")
    print("="*60)

    results = {}

    for res, template_path in test_templates.items():
        if not template_path.exists():
            print(f"\n[{res}] ✗ 템플릿 파일 없음: {template_path}")
            results[res] = "파일 없음"
            continue

        print(f"\n[{res}] 테스트 중...")
        print(f"  템플릿: {template_path}")

        try:
            # 신뢰도 0.8로 탐색
            location = pyautogui.locateOnScreen(str(template_path), confidence=0.8)

            if location:
                print(f"  ✓ 인식 성공! 위치: {location}")
                results[res] = "성공"
            else:
                print(f"  ✗ 인식 실패 (신뢰도 0.8)")

                # 신뢰도 낮춰서 재시도
                location = pyautogui.locateOnScreen(str(template_path), confidence=0.6)
                if location:
                    print(f"  ⚠ 신뢰도 0.6으로 인식됨: {location}")
                    results[res] = "낮은 신뢰도"
                else:
                    print(f"  ✗ 신뢰도 0.6에서도 인식 실패")
                    results[res] = "실패"

        except Exception as e:
            print(f"  ✗ 오류: {e}")
            results[res] = f"오류: {e}"

    # 결과 요약
    print("\n" + "="*60)
    print("테스트 결과 요약")
    print("="*60)
    print(f"\n현재 해상도: {current_res}")
    print()

    for res, result in results.items():
        status = "✓" if result == "성공" else ("⚠" if result == "낮은 신뢰도" else "✗")
        print(f"{status} {res}: {result}")

    print("\n" + "="*60)
    print("결론")
    print("="*60)

    if current_res in results and results[current_res] == "성공":
        print(f"✓ 같은 해상도 템플릿은 잘 작동합니다.")

    # 다른 해상도 템플릿 확인
    other_res_works = any(
        res != current_res and result == "성공"
        for res, result in results.items()
    )

    if other_res_works:
        print(f"✓ 다른 해상도 템플릿도 작동합니다!")
        print(f"  → 해상도별로 템플릿을 나눌 필요가 없을 수 있습니다.")
    else:
        print(f"✗ 다른 해상도 템플릿은 작동하지 않습니다.")
        print(f"  → 해상도별로 별도의 템플릿이 필요합니다.")


if __name__ == "__main__":
    test_template_compatibility()
