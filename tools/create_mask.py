"""
마스크 이미지 생성 도구

템플릿 이미지에서 마스크를 생성합니다.
마스크는 흰색(255) 영역만 템플릿 매칭에 사용되고, 검은색(0) 영역은 무시됩니다.

사용법:
1. 템플릿 이미지를 준비합니다 (예: character_marker.png)
2. 이 스크립트를 실행합니다
3. 마우스로 무시할 영역을 클릭하거나 드래그합니다
4. 'q' 키를 누르면 마스크가 저장됩니다

키보드 단축키:
- 마우스 좌클릭: 점 추가 (다각형 모드)
- 마우스 드래그: 사각형 선택 (사각형 모드)
- 'm': 모드 전환 (다각형 ↔ 사각형)
- 'c': 현재 선택 초기화
- 'i': 선택 영역 반전 (테두리만 남기기)
- 's': 마스크 저장
- 'q': 종료 및 저장
- 'ESC': 취소 및 종료
"""

import sys
import io
import cv2
import numpy as np
from pathlib import Path

# UTF-8 인코딩 강제 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 전역 변수
drawing = False
mode = 'polygon'  # 'polygon' 또는 'rectangle'
points = []
rect_start = None
mask = None
display_img = None
original_img = None


def mouse_callback(event, x, y, flags, param):
    """마우스 콜백 함수"""
    global drawing, points, rect_start, mask, display_img, mode

    if mode == 'polygon':
        # 다각형 모드
        if event == cv2.EVENT_LBUTTONDOWN:
            points.append((x, y))
            # 점 표시
            cv2.circle(display_img, (x, y), 3, (0, 255, 0), -1)
            # 선 연결
            if len(points) > 1:
                cv2.line(display_img, points[-2], points[-1], (0, 255, 0), 2)
            cv2.imshow('Mask Creator', display_img)

    elif mode == 'rectangle':
        # 사각형 모드
        if event == cv2.EVENT_LBUTTONDOWN:
            drawing = True
            rect_start = (x, y)

        elif event == cv2.EVENT_MOUSEMOVE:
            if drawing:
                temp_img = display_img.copy()
                cv2.rectangle(temp_img, rect_start, (x, y), (0, 255, 0), 2)
                cv2.imshow('Mask Creator', temp_img)

        elif event == cv2.EVENT_LBUTTONUP:
            drawing = False
            points.append([rect_start, (x, y)])
            cv2.rectangle(display_img, rect_start, (x, y), (0, 255, 0), 2)
            cv2.imshow('Mask Creator', display_img)


def create_mask(template_path: Path):
    """
    템플릿 이미지에서 마스크 생성

    Args:
        template_path: 템플릿 이미지 경로
    """
    global mask, display_img, original_img, points, mode

    # 이미지 로드
    img = cv2.imread(str(template_path))
    if img is None:
        print(f"✗ 이미지를 로드할 수 없습니다: {template_path}")
        return None

    print(f"✓ 이미지 로드 성공: {template_path}")
    print(f"  크기: {img.shape[1]}x{img.shape[0]}")

    # 마스크 초기화 (전체 흰색)
    mask = np.ones((img.shape[0], img.shape[1]), dtype=np.uint8) * 255
    display_img = img.copy()
    original_img = img.copy()

    # 윈도우 생성
    cv2.namedWindow('Mask Creator')
    cv2.setMouseCallback('Mask Creator', mouse_callback)

    print("\n" + "="*60)
    print("마스크 생성 도구")
    print("="*60)
    print(f"현재 모드: {mode}")
    print("\n[키보드 단축키]")
    print("  마우스 좌클릭: 점 추가 (다각형 모드) / 사각형 드래그 (사각형 모드)")
    print("  'm': 모드 전환 (다각형 ↔ 사각형)")
    print("  'c': 현재 선택 초기화")
    print("  'i': 선택 영역 반전 (테두리만 남기기)")
    print("  's': 마스크 저장")
    print("  'q': 종료 및 저장")
    print("  'ESC': 취소 및 종료")
    print("="*60)

    while True:
        cv2.imshow('Mask Creator', display_img)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            # 종료 및 저장
            break

        elif key == 27:  # ESC
            # 취소 및 종료
            print("\n마스크 생성 취소됨")
            cv2.destroyAllWindows()
            return None

        elif key == ord('m'):
            # 모드 전환
            mode = 'rectangle' if mode == 'polygon' else 'polygon'
            print(f"\n현재 모드: {mode}")

        elif key == ord('c'):
            # 선택 초기화
            points = []
            display_img = original_img.copy()
            print("\n선택 영역 초기화됨")

        elif key == ord('i'):
            # 선택 영역 반전 (마스크 생성)
            if len(points) > 0:
                if mode == 'polygon' and len(points) >= 3:
                    # 다각형 마스크 생성
                    pts = np.array(points, dtype=np.int32)
                    cv2.fillPoly(mask, [pts], 0)
                    print(f"\n✓ 다각형 영역이 마스크에서 제거됨 ({len(points)}개 점)")

                elif mode == 'rectangle' and len(points) > 0:
                    # 사각형 마스크 생성
                    for rect in points:
                        if isinstance(rect, list) and len(rect) == 2:
                            cv2.rectangle(mask, rect[0], rect[1], 0, -1)
                    print(f"\n✓ {len(points)}개 사각형 영역이 마스크에서 제거됨")

                # 마스크 미리보기
                preview = cv2.addWeighted(original_img, 0.7, cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR), 0.3, 0)
                display_img = preview
                cv2.imshow('Mask Creator', display_img)

            else:
                print("\n⚠ 선택된 영역이 없습니다")

        elif key == ord('s'):
            # 마스크 저장
            mask_path = template_path.parent / f"{template_path.stem}_mask.png"
            cv2.imwrite(str(mask_path), mask)
            print(f"\n✓ 마스크 저장됨: {mask_path}")

    # 최종 마스크 저장
    if len(points) > 0:
        if mode == 'polygon' and len(points) >= 3:
            pts = np.array(points, dtype=np.int32)
            cv2.fillPoly(mask, [pts], 0)
        elif mode == 'rectangle' and len(points) > 0:
            for rect in points:
                if isinstance(rect, list) and len(rect) == 2:
                    cv2.rectangle(mask, rect[0], rect[1], 0, -1)

    mask_path = template_path.parent / f"{template_path.stem}_mask.png"
    cv2.imwrite(str(mask_path), mask)
    print(f"\n✓ 최종 마스크 저장됨: {mask_path}")

    # 마스크 미리보기 저장
    preview_path = template_path.parent / f"{template_path.stem}_mask_preview.png"
    preview = np.hstack([original_img, cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)])
    cv2.imwrite(str(preview_path), preview)
    print(f"✓ 마스크 미리보기 저장됨: {preview_path}")

    cv2.destroyAllWindows()
    return mask_path


def main():
    """메인 함수"""
    print("="*60)
    print("마스크 이미지 생성 도구")
    print("="*60)

    # 템플릿 경로 입력
    template_input = input("\n템플릿 이미지 경로를 입력하세요: ").strip()

    if not template_input:
        print("✗ 경로가 입력되지 않았습니다")
        return

    template_path = Path(template_input)

    if not template_path.exists():
        print(f"✗ 파일이 존재하지 않습니다: {template_path}")
        return

    # 마스크 생성
    mask_path = create_mask(template_path)

    if mask_path:
        print("\n" + "="*60)
        print("✓ 마스크 생성 완료!")
        print(f"  템플릿: {template_path}")
        print(f"  마스크: {mask_path}")
        print("="*60)


if __name__ == "__main__":
    main()
