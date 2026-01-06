"""
다양한 PSM 모드로 OCR 테스트

Tesseract의 Page Segmentation Mode를 변경하면서 최적 설정 찾기
"""

import sys
from pathlib import Path
from PIL import Image

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.ocr import OCRReader


def main():
    print("=" * 70)
    print("PSM 모드별 OCR 테스트")
    print("=" * 70)
    print()

    # 이미지 로드
    image_path = project_root / "assets" / "templates" / "buttons" / "deploy_button.png"
    image = Image.open(image_path)

    reader = OCRReader()

    # 전처리
    preprocessed = reader.preprocess_image(image)

    # PSM 모드별 테스트
    psm_modes = {
        3: "완전 자동 페이지 분할 (기본)",
        4: "단일 컬럼 가변 크기 텍스트",
        6: "단일 텍스트 블록",
        7: "단일 텍스트 라인",
        8: "단일 단어",
        11: "희박한 텍스트 (순서 무관)",
        13: "원시 라인 (텍스트 라인 탐지 없음)",
    }

    print("원본 이미지 테스트:")
    print("-" * 70)
    for psm, description in psm_modes.items():
        config = f'--psm {psm}'
        try:
            import pytesseract
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

            # 한글만
            text_kor = pytesseract.image_to_string(image, lang='kor', config=config)
            # 한글+영어
            text_both = pytesseract.image_to_string(image, lang='kor+eng', config=config)

            print(f"PSM {psm} ({description}):")
            print(f"  한글: '{text_kor.strip()}'")
            print(f"  한글+영어: '{text_both.strip()}'")
            print()
        except Exception as e:
            print(f"PSM {psm} 실패: {e}")
            print()

    print("\n" + "=" * 70)
    print("전처리된 이미지 테스트:")
    print("-" * 70)
    for psm, description in psm_modes.items():
        config = f'--psm {psm}'
        try:
            import pytesseract

            # 한글만
            text_kor = pytesseract.image_to_string(preprocessed, lang='kor', config=config)
            # 한글+영어
            text_both = pytesseract.image_to_string(preprocessed, lang='kor+eng', config=config)

            print(f"PSM {psm} ({description}):")
            print(f"  한글: '{text_kor.strip()}'")
            print(f"  한글+영어: '{text_both.strip()}'")
            print()
        except Exception as e:
            print(f"PSM {psm} 실패: {e}")
            print()


if __name__ == "__main__":
    main()
