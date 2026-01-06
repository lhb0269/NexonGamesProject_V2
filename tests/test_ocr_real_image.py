"""실제 게임 이미지에서 OCR 테스트

게임 템플릿 이미지를 사용하여 OCR 기능을 테스트합니다.
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PIL import Image
from config.settings import BUTTONS_DIR, UI_DIR, ICONS_DIR


def test_image_ocr(image_path: Path, description: str = ""):
    """이미지에서 OCR 테스트

    Args:
        image_path: 이미지 파일 경로
        description: 이미지 설명
    """
    print("\n" + "="*60)
    print(f"이미지 OCR 테스트: {description or image_path.name}")
    print("="*60)

    # 이미지 존재 확인
    if not image_path.exists():
        print(f"✗ 이미지 파일이 존재하지 않습니다: {image_path}")
        return None

    print(f"✓ 이미지 파일 존재: {image_path}")

    try:
        # 이미지 로드
        img = Image.open(image_path)
        print(f"✓ 이미지 로드 성공 (크기: {img.size})")

        # OCR 모듈 임포트
        from src.ocr import OCREngine, NumberReader, TextReader

        # 1. OCREngine으로 직접 텍스트 추출
        print("\n[1] OCREngine - 일반 텍스트 추출")
        ocr = OCREngine(lang='eng')
        text = ocr.extract_text(img, preprocess=True)
        print(f"  결과: '{text}'")

        # 2. OCREngine - 숫자 추출 시도
        print("\n[2] OCREngine - 숫자 추출")
        number = ocr.extract_number(img, preprocess=True)
        print(f"  결과: {number}")

        # 3. TextReader로 텍스트 추출
        print("\n[3] TextReader - 텍스트 추출")
        text_reader = TextReader()
        text_result = text_reader.read_text(img)
        print(f"  결과: '{text_result}'")

        # 4. NumberReader로 숫자 추출
        print("\n[4] NumberReader - 정수 추출")
        number_reader = NumberReader()
        number_result = number_reader.read_integer(img)
        print(f"  결과: {number_result}")

        # 5. 전처리 적용/미적용 비교
        print("\n[5] 전처리 비교")
        print("  - 전처리 없음:")
        text_no_prep = ocr.extract_text(img, preprocess=False)
        print(f"    결과: '{text_no_prep}'")

        print("  - 전처리 적용:")
        text_with_prep = ocr.extract_text(img, preprocess=True)
        print(f"    결과: '{text_with_prep}'")

        return {
            "text": text,
            "number": number,
            "text_reader": text_result,
            "number_reader": number_result
        }

    except Exception as e:
        print(f"✗ OCR 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """메인 함수"""
    print("\n실제 게임 이미지 OCR 테스트")
    print("\n이 테스트는 실제 게임 템플릿 이미지에서 텍스트/숫자를 읽습니다.")
    print("Tesseract OCR이 설치되어 있어야 합니다.\n")

    # Tesseract 설치 확인
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        print("✓ Tesseract OCR 설치 확인 완료\n")
    except:
        print("✗ Tesseract OCR이 설치되지 않았습니다")
        print("  설치: https://github.com/UB-Mannheim/tesseract/wiki\n")
        return

    # 테스트할 이미지 목록 (존재하는 것만)
    test_images = [
        (BUTTONS_DIR / "deploy_button.png", "출격 버튼"),
        (BUTTONS_DIR / "mission_start_button.png", "임무 개시 버튼"),
        (BUTTONS_DIR / "phase_end_button.png", "Phase 종료 버튼"),
        (UI_DIR / "victory.png", "Victory 화면"),
        (UI_DIR / "damage_report.png", "데미지 기록 창"),
    ]

    results = {}

    for image_path, description in test_images:
        result = test_image_ocr(image_path, description)
        if result:
            results[description] = result

    # 결과 요약
    print("\n" + "="*60)
    print("테스트 결과 요약")
    print("="*60)

    for desc, result in results.items():
        print(f"\n[{desc}]")
        print(f"  텍스트: '{result['text']}'")
        print(f"  숫자: {result['number']}")

    if not results:
        print("\n⚠ 테스트할 이미지가 없거나 모두 실패했습니다")
        print("\n확인사항:")
        print("  1. assets/templates/ 폴더에 이미지가 있나요?")
        print("  2. Tesseract OCR이 제대로 설치되었나요?")
    else:
        print(f"\n✓ {len(results)}개 이미지 테스트 완료")
        print("\n참고:")
        print("  - 버튼 이미지는 텍스트보다 아이콘이 많아 OCR 정확도가 낮을 수 있습니다")
        print("  - 데미지 기록 창처럼 명확한 숫자/텍스트가 있는 이미지가 OCR에 적합합니다")


if __name__ == "__main__":
    main()
