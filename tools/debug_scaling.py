"""스케일링 디버깅 도구

스케일링된 템플릿 이미지를 저장해서 직접 확인
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PIL import Image
import pyautogui
from config.settings import TEMPLATES_DIR


def debug_scaling():
    """스케일링 테스트 및 저장"""

    print("\n" + "="*60)
    print("스케일링 디버깅")
    print("="*60)

    # 현재 화면 해상도
    screen_size = pyautogui.size()
    current_res = f"{screen_size.width}x{screen_size.height}"
    print(f"\n현재 화면 해상도: {current_res}")

    # 2560x1440 템플릿
    template_2560 = TEMPLATES_DIR / "2560x1440" / "buttons" / "deploy_button.png"

    if not template_2560.exists():
        print(f"\n✗ 템플릿이 없습니다: {template_2560}")
        return

    print(f"\n원본 템플릿: {template_2560}")

    # 원본 이미지 로드
    img = Image.open(template_2560)
    print(f"원본 크기: {img.width}x{img.height} 픽셀")

    # 스케일 비율 계산
    template_width = 2560
    template_height = 1440
    screen_width = screen_size.width
    screen_height = screen_size.height

    scale_x = screen_width / template_width
    scale_y = screen_height / template_height

    print(f"\n스케일 비율:")
    print(f"  X: {scale_x:.4f} ({template_width} → {screen_width})")
    print(f"  Y: {scale_y:.4f} ({template_height} → {screen_height})")

    # 스케일링
    new_width = int(img.width * scale_x)
    new_height = int(img.height * scale_y)

    print(f"\n스케일링 후 크기: {new_width}x{new_height} 픽셀")

    scaled_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # 저장
    output_dir = TEMPLATES_DIR / "debug"
    output_dir.mkdir(exist_ok=True)

    output_path = output_dir / f"deploy_button_scaled_{current_res}.png"
    scaled_img.save(output_path)

    print(f"\n✓ 스케일링된 이미지 저장: {output_path}")
    print("\n이제 이 이미지를 열어서 게임 화면의 버튼과 비교해보세요.")
    print("크기가 비슷한지 확인하세요.")

    # 실제 테스트
    print("\n" + "="*60)
    print("스케일링된 이미지로 인식 테스트")
    print("="*60)
    print("\n준비:")
    print("  1. 블루 아카이브 실행")
    print("  2. '출격' 버튼이 보이는 화면으로 이동")
    print("\n5초 후 테스트 시작...\n")

    import time
    for i in range(5, 0, -1):
        print(f"{i}...")
        time.sleep(1)

    print("\n[테스트 1] 원본 이미지 (2560x1440)")
    try:
        location = pyautogui.locateOnScreen(str(template_2560), confidence=0.8)
        if location:
            print(f"  ✓ 인식 성공: {location}")
        else:
            print(f"  ✗ 인식 실패")
    except Exception as e:
        print(f"  ✗ 오류: {e}")

    print(f"\n[테스트 2] 스케일링된 이미지 ({current_res})")
    try:
        location = pyautogui.locateOnScreen(str(output_path), confidence=0.8)
        if location:
            print(f"  ✓ 인식 성공: {location}")
        else:
            print(f"  ✗ 인식 실패 (신뢰도 0.8)")

            # 신뢰도 낮춰서 재시도
            location = pyautogui.locateOnScreen(str(output_path), confidence=0.6)
            if location:
                print(f"  ⚠ 신뢰도 0.6에서 인식됨: {location}")
            else:
                print(f"  ✗ 신뢰도 0.6에서도 실패")

                # 더 낮춰서
                location = pyautogui.locateOnScreen(str(output_path), confidence=0.4)
                if location:
                    print(f"  ⚠ 신뢰도 0.4에서 인식됨: {location}")
                else:
                    print(f"  ✗ 신뢰도 0.4에서도 실패")

    except Exception as e:
        print(f"  ✗ 오류: {e}")

    print("\n" + "="*60)
    print("결론:")
    print("="*60)
    print(f"\n1. 스케일링된 이미지를 확인하세요: {output_path}")
    print(f"2. 게임 화면의 '출격' 버튼과 크기를 비교하세요")
    print(f"3. 크기가 다르다면 게임 UI가 고정 크기일 가능성이 있습니다")
    print(f"4. 그 경우 1920x1080에서 직접 캡처해야 합니다")


if __name__ == "__main__":
    debug_scaling()
