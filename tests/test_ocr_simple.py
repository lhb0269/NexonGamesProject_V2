"""
OCR 모듈 간단 테스트

Tesseract 설치 없이도 실행 가능한 기본 테스트
"""

import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_module_import():
    """OCR 모듈 import 테스트"""
    try:
        from src.ocr import OCRReader
        print("✓ OCRReader import 성공")
        return True
    except ImportError as e:
        print(f"✗ OCRReader import 실패: {e}")
        return False


def test_class_structure():
    """OCRReader 클래스 구조 테스트"""
    try:
        from src.ocr import OCRReader
    except ImportError:
        print("✗ pytesseract 설치 필요")
        return False

    # 메서드 존재 확인
    required_methods = [
        # 이미지 전처리
        'preprocess_image',

        # 텍스트 읽기
        'read_text',
        'read_student_name',
        'batch_read_student_names',

        # 숫자 읽기
        'read_integer',
        'read_cost_value',
        'read_damage_value',
        'compare_cost_values',
        'batch_read_damages',

        # 고급 기능
        'extract_from_region',
        'extract_student_data',
    ]

    missing_methods = []
    for method in required_methods:
        if not hasattr(OCRReader, method):
            missing_methods.append(method)

    if missing_methods:
        print(f"✗ 누락된 메서드: {', '.join(missing_methods)}")
        return False
    else:
        print(f"✓ 모든 메서드 존재 확인 ({len(required_methods)}개)")
        return True


def test_dependencies():
    """의존성 패키지 설치 확인"""
    dependencies = {
        'PIL': 'Pillow',
        'cv2': 'opencv-python',
        'numpy': 'numpy',
        'pytesseract': 'pytesseract',
    }

    all_installed = True
    for module, package in dependencies.items():
        try:
            __import__(module)
            print(f"✓ {package} 설치됨")
        except ImportError:
            print(f"✗ {package} 미설치 (pip install {package})")
            all_installed = False

    return all_installed


def main():
    """전체 테스트 실행"""
    print("=" * 50)
    print("OCR 모듈 간단 테스트")
    print("=" * 50)
    print()

    tests = [
        ("모듈 import", test_module_import),
        ("의존성 패키지", test_dependencies),
        ("클래스 구조", test_class_structure),
    ]

    results = []
    for name, test_func in tests:
        print(f"[{name}]")
        result = test_func()
        results.append(result)
        print()

    # 결과 요약
    print("=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"테스트 결과: {passed}/{total} 통과")
    print("=" * 50)

    if passed == total:
        print("✓ 모든 테스트 통과!")
    else:
        print(f"✗ {total - passed}개 테스트 실패")


if __name__ == "__main__":
    main()
