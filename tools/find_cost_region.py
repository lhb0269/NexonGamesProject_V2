"""
코스트 영역 자동 탐지 도구 (대화형)

캡처된 전투 화면 이미지를 열고, 마우스로 코스트 영역을 선택하면
자동으로 좌표를 계산해줍니다.
"""

import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import tkinter as tk
from tkinter import filedialog

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class RegionSelector:
    """마우스로 영역 선택하는 GUI"""

    def __init__(self, image_path):
        self.image_path = image_path
        self.image = Image.open(image_path)
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.rect_id = None

        # Tkinter 윈도우
        self.root = tk.Tk()
        self.root.title("코스트 영역 선택 - 드래그하여 코스트 숫자 영역 선택")

        # Canvas 크기 조정 (이미지가 너무 크면 화면에 맞춤)
        max_width = 1600
        max_height = 900
        img_width, img_height = self.image.size

        self.scale = 1.0
        if img_width > max_width or img_height > max_height:
            scale_x = max_width / img_width
            scale_y = max_height / img_height
            self.scale = min(scale_x, scale_y)

        display_width = int(img_width * self.scale)
        display_height = int(img_height * self.scale)

        # 이미지 표시 (Canvas 전에 ImageTk 생성)
        from PIL import ImageTk
        display_image = self.image.resize((display_width, display_height))
        self.photo = ImageTk.PhotoImage(display_image, master=self.root)

        # Canvas 생성
        self.canvas = tk.Canvas(
            self.root,
            width=display_width,
            height=display_height
        )
        self.canvas.pack()

        # 이미지 표시
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

        # 마우스 이벤트 바인딩
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        # 안내 텍스트
        info_label = tk.Label(
            self.root,
            text="마우스 드래그로 코스트 숫자 영역을 선택하세요 (우측 상단의 현재 코스트 숫자)",
            font=("Arial", 12)
        )
        info_label.pack(pady=10)

    def on_press(self, event):
        """마우스 버튼 눌렀을 때"""
        self.start_x = int(event.x / self.scale)
        self.start_y = int(event.y / self.scale)

    def on_drag(self, event):
        """마우스 드래그 중"""
        if self.rect_id:
            self.canvas.delete(self.rect_id)

        current_x = event.x
        current_y = event.y
        self.rect_id = self.canvas.create_rectangle(
            self.start_x * self.scale,
            self.start_y * self.scale,
            current_x,
            current_y,
            outline="red",
            width=2
        )

    def on_release(self, event):
        """마우스 버튼 뗐을 때"""
        self.end_x = int(event.x / self.scale)
        self.end_y = int(event.y / self.scale)

        # 좌표 정규화 (좌상단이 항상 작은 값)
        x1 = min(self.start_x, self.end_x)
        y1 = min(self.start_y, self.end_y)
        x2 = max(self.start_x, self.end_x)
        y2 = max(self.start_y, self.end_y)

        print()
        print("=" * 70)
        print("선택된 영역 좌표:")
        print("=" * 70)
        print(f"좌측 상단: ({x1}, {y1})")
        print(f"우측 하단: ({x2}, {y2})")
        print(f"영역 크기: {x2 - x1}x{y2 - y1}")
        print()
        print("config/ocr_regions.py 에 아래 좌표를 복사하세요:")
        print("-" * 70)
        print(f"BATTLE_COST_VALUE_REGION = ({x1}, {y1}, {x2}, {y2})")
        print("=" * 70)
        print()

        # 선택 영역 미리보기 저장
        cropped = self.image.crop((x1, y1, x2, y2))
        preview_path = Path(self.image_path).parent / "cost_region_preview.png"
        cropped.save(preview_path)
        print(f"✓ 선택 영역 미리보기 저장: {preview_path}")
        print()

    def run(self):
        """GUI 실행"""
        self.root.mainloop()


def main():
    print("=" * 70)
    print("코스트 영역 선택 도구")
    print("=" * 70)
    print()
    print("사용 방법:")
    print("1. 전투 화면 스크린샷 파일 선택")
    print("2. 열린 창에서 마우스로 코스트 숫자 영역 드래그")
    print("3. 터미널에 출력된 좌표를 config/ocr_regions.py에 복사")
    print()

    # 파일 선택 대화상자
    root = tk.Tk()
    root.withdraw()

    # 기본 경로
    default_dir = project_root / "logs" / "ocr_calibration"
    if not default_dir.exists():
        default_dir = project_root / "logs"

    file_path = filedialog.askopenfilename(
        title="전투 화면 스크린샷 선택",
        initialdir=str(default_dir),
        filetypes=[
            ("PNG 이미지", "*.png"),
            ("모든 이미지", "*.png *.jpg *.jpeg"),
            ("모든 파일", "*.*")
        ]
    )

    if not file_path:
        print("파일이 선택되지 않았습니다. 종료합니다.")
        return

    print(f"선택된 파일: {file_path}")
    print()

    # 영역 선택 GUI 시작
    selector = RegionSelector(file_path)
    selector.run()


if __name__ == "__main__":
    main()
