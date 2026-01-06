"""
deploy_button.png OCR 테스트

실제 게임 템플릿 이미지에서 텍스트를 읽는 테스트
Tesseract OCR 설치 필요
"""

import sys
from pathlib import Path
from PIL import Image

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.ocr import OCRReader


def main():
    print("=" * 60)
    print("deploy_button.png OCR 테스트")
    print("=" * 60)
    print()

    # 이미지 파일 경로
    image_path = project_root / "assets" / "templates" / "buttons" / "deploy_button.png"

    if not image_path.exists():
        print(f"✗ 이미지 파일을 찾을 수 없습니다: {image_path}")
        return

    print(f"이미지 경로: {image_path}")
    print(f"파일 크기: {image_path.stat().st_size:,} bytes")
    print()

    # 이미지 로드
    try:
        image = Image.open(image_path)
        print(f"이미지 크기: {image.size[0]}x{image.size[1]}")
        print(f"이미지 모드: {image.mode}")
        print()
    except Exception as e:
        print(f"✗ 이미지 로드 실패: {e}")
        return

    # OCRReader 초기화
    try:
        reader = OCRReader()
        print("✓ OCRReader 초기화 성공")
        print()
    except Exception as e:
        print(f"✗ OCRReader 초기화 실패: {e}")
        print()
        print("Tesseract OCR 설치 필요:")
        print("https://github.com/UB-Mannheim/tesseract/wiki")
        return

    # 테스트 1: 한글 텍스트 읽기
    print("-" * 60)
    print("[테스트 1] 한글 텍스트 읽기 (전처리 활성화)")
    print("-" * 60)
    try:
        text = reader.read_text(image, lang='kor', preprocess=True)
        print(f"결과: '{text}'")
        print(f"길이: {len(text)} 문자")
    except Exception as e:
        print(f"✗ 읽기 실패: {e}")
    print()

    # 테스트 2: 한글+영어 텍스트 읽기
    print("-" * 60)
    print("[테스트 2] 한글+영어 텍스트 읽기 (전처리 활성화)")
    print("-" * 60)
    try:
        text = reader.read_text(image, lang='kor+eng', preprocess=True)
        print(f"결과: '{text}'")
        print(f"길이: {len(text)} 문자")
    except Exception as e:
        print(f"✗ 읽기 실패: {e}")
    print()

    # 테스트 3: 전처리 비활성화
    print("-" * 60)
    print("[테스트 3] 한글+영어 텍스트 읽기 (전처리 비활성화)")
    print("-" * 60)
    try:
        text = reader.read_text(image, lang='kor+eng', preprocess=False)
        print(f"결과: '{text}'")
        print(f"길이: {len(text)} 문자")
    except Exception as e:
        print(f"✗ 읽기 실패: {e}")
    print()

    # 테스트 4: 영어만 읽기
    print("-" * 60)
    print("[테스트 4] 영어 텍스트 읽기 (Space 부분)")
    print("-" * 60)
    try:
        text = reader.read_text(image, lang='eng', preprocess=True)
        print(f"결과: '{text}'")
        print(f"길이: {len(text)} 문자")
    except Exception as e:
        print(f"✗ 읽기 실패: {e}")
    print()

    # 테스트 5: 전처리된 이미지 확인
    print("-" * 60)
    print("[테스트 5] 전처리 이미지 저장 (디버깅용)")
    print("-" * 60)
    try:
        preprocessed = reader.preprocess_image(
            image,
            grayscale=True,
            threshold=True,
            denoise=False,
            scale_factor=2.0
        )
        output_path = project_root / "logs" / "deploy_button_preprocessed.png"
        output_path.parent.mkdir(exist_ok=True)
        preprocessed.save(output_path)
        print(f"✓ 전처리 이미지 저장: {output_path}")
    except Exception as e:
        print(f"✗ 전처리 실패: {e}")
    print()

    print("=" * 60)
    print("테스트 완료")
    print("=" * 60)


if __name__ == "__main__":
    main()
