"""해상도별 템플릿 복사 도구

다른 해상도용 템플릿을 생성하기 위해 기존 템플릿을 복사합니다.
실제로는 각 해상도에 맞게 새로 캡처해야 하지만, 테스트용으로 사용할 수 있습니다.
"""

import shutil
from pathlib import Path
import sys

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import TEMPLATES_DIR


def copy_templates(source_resolution, target_resolution):
    """템플릿을 다른 해상도로 복사

    Args:
        source_resolution: 원본 해상도 (예: "1920x1080")
        target_resolution: 대상 해상도 (예: "2560x1440")
    """
    source_dir = TEMPLATES_DIR / source_resolution
    target_dir = TEMPLATES_DIR / target_resolution

    print(f"\n템플릿 복사: {source_resolution} → {target_resolution}")
    print(f"원본: {source_dir}")
    print(f"대상: {target_dir}")
    print("="*60)

    if not source_dir.exists():
        print(f"✗ 오류: 원본 디렉토리가 존재하지 않습니다: {source_dir}")
        return False

    # 대상 디렉토리 생성
    target_dir.mkdir(parents=True, exist_ok=True)

    # 하위 디렉토리 복사
    subdirs = ["buttons", "icons", "ui"]

    for subdir in subdirs:
        source_subdir = source_dir / subdir
        target_subdir = target_dir / subdir

        if not source_subdir.exists():
            print(f"⚠ 경고: {subdir} 디렉토리가 원본에 없습니다.")
            continue

        # 대상 하위 디렉토리 생성
        target_subdir.mkdir(parents=True, exist_ok=True)

        # 파일 복사
        copied_files = 0
        for file_path in source_subdir.glob("*.png"):
            target_file = target_subdir / file_path.name
            shutil.copy2(file_path, target_file)
            print(f"✓ 복사: {subdir}/{file_path.name}")
            copied_files += 1

        if copied_files == 0:
            print(f"⚠ {subdir}에 복사할 파일이 없습니다.")

    print("="*60)
    print(f"✓ 템플릿 복사 완료!")
    print(f"\n⚠ 주의: 복사된 템플릿은 {source_resolution} 해상도용입니다.")
    print(f"   {target_resolution} 해상도에서 정확하게 작동하지 않을 수 있습니다.")
    print(f"   가능하면 {target_resolution} 해상도에서 직접 캡처하세요.")

    return True


def main():
    """메인 함수"""
    print("\n해상도별 템플릿 복사 도구")
    print("="*60)

    # 사용 가능한 해상도 표시
    print("\n사용 가능한 해상도:")
    print("1. 1920x1080 (Full HD)")
    print("2. 2560x1440 (QHD)")
    print("3. 3840x2160 (4K UHD)")

    # 원본 해상도 입력
    print("\n원본 해상도를 선택하세요:")
    source = input("원본 (예: 1920x1080): ").strip()

    if not source:
        source = "1920x1080"
        print(f"기본값 사용: {source}")

    # 대상 해상도 입력
    print("\n대상 해상도를 선택하세요:")
    target = input("대상 (예: 2560x1440): ").strip()

    if not target:
        target = "2560x1440"
        print(f"기본값 사용: {target}")

    # 복사 실행
    copy_templates(source, target)


if __name__ == "__main__":
    main()
