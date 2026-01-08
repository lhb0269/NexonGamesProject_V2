"""블루 아카이브 자동화 테스트 GUI

tkinter 기반 테스트 실행 및 모니터링 GUI
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import sys
import io
from pathlib import Path
from datetime import datetime
from config.settings import (
    CURRENT_RESOLUTION, SUPPORTED_RESOLUTIONS,
    save_display_settings, get_resolution_dir
)


class TestRunnerGUI:
    """테스트 실행 GUI 메인 클래스"""

    def __init__(self, root):
        self.root = root

        self.root.title("블루 아카이브 자동화 테스트 실행기")

        self.root.geometry("1200x700")

        # 테스트 실행 상태
        self.is_running = False
        self.current_test = None

        # 현재 해상도 설정
        self.current_resolution = CURRENT_RESOLUTION

        # GUI 컴포넌트 초기화
        self.setup_ui()

    def setup_ui(self):
        """UI 레이아웃 구성"""

        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 그리드 가중치 설정
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # 상단 헤더 프레임
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky=(tk.W, tk.E))
        header_frame.columnconfigure(0, weight=1)

        # 상단 타이틀
        title_label = ttk.Label(
            header_frame,
            text="블루 아카이브 Normal 1-4 자동화 테스트",
            font=("TkDefaultFont", 16, "bold")
        )
        title_label.grid(row=0, column=0, sticky=tk.W)

        # 디스플레이 설정 버튼
        try:
            display_btn = tk.Button(
                header_frame,
                text=f"디스플레이: {self.current_resolution}",  # 이모지 제거
                command=self.open_display_settings,
                bg="#607D8B",
                fg="white",
                cursor="hand2",
                relief=tk.RAISED,
                borderwidth=2,
                padx=10,
                pady=5
            )
            display_btn.grid(row=0, column=1, sticky=tk.E)
            self.display_btn = display_btn
        except Exception as e:
            raise

        # 왼쪽 패널: 테스트 항목 버튼들
        left_frame = ttk.LabelFrame(main_frame, text="테스트 항목", padding="10")
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))

        # 오른쪽 패널: 로그 출력
        right_frame = ttk.LabelFrame(main_frame, text="실시간 로그", padding="10")
        right_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)

        # 테스트 항목 버튼들
        self.create_test_buttons(left_frame)

        # 로그 출력 창
        self.create_log_panel(right_frame)

        # 하단 상태바
        self.create_status_bar(main_frame)

    def create_test_buttons(self, parent):
        """테스트 항목 버튼 생성"""

        # 테스트 목록 정의
        tests = [
            {
                "name": "기본 모듈 테스트",
                "description": "TemplateMatcher, GameController 등 기본 모듈 동작 확인",
                "module": "tests.test_modules",
                "color": "#4CAF50"
            },
            {
                "name": "단계 1-2.5: 스테이지 진입",
                "description": "시작 발판 → 편성 → 출격 → 맵 → 임무 개시",
                "module": "tests.test_partial_stage",
                "color": "#2196F3"
            },
            {
                "name": "단계 3: 발판 이동",
                "description": "적 발판/빈 발판 클릭 및 이동 테스트",
                "module": "tests.test_tile_movement",
                "color": "#FF9800"
            },
            {
                "name": "스킬 코스트 OCR 테스트",
                "description": "전투 중 스킬 버튼 코스트 및 현재 코스트 인식 테스트",
                "module": "tests.test_skill_cost_ocr",
                "color": "#00BCD4"
            },
            {
                "name": "스킬 사용 시스템 테스트",
                "description": "스킬 사용 및 코스트 소모 검증 (단일/다중 스킬)",
                "module": "tests.test_skill_usage",
                "color": "#673AB7"
            },
            {
                "name": "단계 6: 전투 결과 확인",
                "description": "Victory → 통계 → 데미지 기록 → 랭크 획득",
                "module": "tests.test_battle_result",
                "color": "#9C27B0"
            },
            {
                "name": "전체 플로우 실행",
                "description": "Normal 1-4 전체 자동 플레이 (단계 1-6)",
                "module": "tests.test_full_stage",
                "color": "#F44336"
            }
        ]

        # 버튼 생성
        for idx, test in enumerate(tests):
            # 버튼 프레임
            btn_frame = ttk.Frame(parent)
            btn_frame.grid(row=idx, column=0, pady=5, sticky=(tk.W, tk.E))

            # 버튼
            btn = tk.Button(
                btn_frame,
                text=test["name"],
                command=lambda t=test: self.run_test(t),
                bg=test["color"],
                fg="white",
                font=("TkDefaultFont", 10, "bold"),
                height=2,
                cursor="hand2",
                relief=tk.RAISED,
                borderwidth=2
            )
            btn.pack(fill=tk.X, pady=2)

            # 설명 레이블
            desc_label = ttk.Label(
                btn_frame,
                text=test["description"],
                font=("TkDefaultFont", 8),
                foreground="gray"
            )
            desc_label.pack(fill=tk.X)

            # 구분선
            if idx < len(tests) - 1:
                ttk.Separator(parent, orient=tk.HORIZONTAL).grid(
                    row=idx + 10, column=0, sticky=(tk.W, tk.E), pady=10
                )

        # 전체 중지 버튼
        stop_btn = tk.Button(
            parent,
            text="⏹ 테스트 중지",
            command=self.stop_test,
            bg="#607D8B",
            fg="white",
            font=("TkDefaultFont", 10, "bold"),
            height=2,
            cursor="hand2",
            state=tk.DISABLED
        )
        stop_btn.grid(row=len(tests) + 20, column=0, pady=20, sticky=(tk.W, tk.E))
        self.stop_btn = stop_btn

    def create_log_panel(self, parent):
        """로그 출력 패널 생성"""

        # 로그 텍스트 위젯 (스크롤 가능)
        self.log_text = scrolledtext.ScrolledText(
            parent,
            wrap=tk.WORD,
            font=("Consolas", 9),
            bg="#1E1E1E",
            fg="#D4D4D4",
            insertbackground="white",
            state=tk.DISABLED
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 태그 스타일 정의
        self.log_text.tag_config("success", foreground="#4CAF50", font=("Consolas", 9, "bold"))
        self.log_text.tag_config("error", foreground="#F44336", font=("Consolas", 9, "bold"))
        self.log_text.tag_config("warning", foreground="#FF9800", font=("Consolas", 9, "bold"))
        self.log_text.tag_config("info", foreground="#2196F3", font=("Consolas", 9, "bold"))
        self.log_text.tag_config("header", foreground="#00BCD4", font=("Consolas", 10, "bold"))

        # 로그 지우기 버튼
        clear_btn = ttk.Button(
            parent,
            text="로그 지우기",
            command=self.clear_log
        )
        clear_btn.grid(row=1, column=0, pady=(5, 0), sticky=tk.E)

    def create_status_bar(self, parent):
        """하단 상태바 생성"""

        status_frame = ttk.Frame(parent)
        status_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0), sticky=(tk.W, tk.E))

        # 상태 레이블
        self.status_label = ttk.Label(
            status_frame,
            text="준비",
            font=("TkDefaultFont", 9)
        )
        self.status_label.pack(side=tk.LEFT)

        # 진행 바
        self.progress_bar = ttk.Progressbar(
            status_frame,
            mode='indeterminate',
            length=200
        )
        self.progress_bar.pack(side=tk.RIGHT, padx=(10, 0))

    def log(self, message, tag=None):
        """로그 메시지 추가"""

        self.log_text.config(state=tk.NORMAL)

        timestamp = datetime.now().strftime("%H:%M:%S")

        if tag:
            self.log_text.insert(tk.END, f"[{timestamp}] ", "info")
            self.log_text.insert(tk.END, f"{message}\n", tag)
        else:
            self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")

        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def clear_log(self):
        """로그 지우기"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

    def update_status(self, message):
        """상태바 업데이트"""
        self.status_label.config(text=message)

    def run_test(self, test_info):
        """테스트 실행"""

        if self.is_running:
            self.log("⚠ 테스트가 이미 실행 중입니다.", "warning")
            return

        self.is_running = True
        self.current_test = test_info
        self.stop_btn.config(state=tk.NORMAL)

        # 로그 초기화
        self.clear_log()

        # 헤더 출력
        self.log("="*60, "header")
        self.log(f"테스트 시작: {test_info['name']}", "header")
        self.log("="*60, "header")
        self.log(f"설명: {test_info['description']}", "info")
        self.log(f"모듈: {test_info['module']}", "info")
        self.log("")

        # 상태 업데이트
        self.update_status(f"실행 중: {test_info['name']}")
        self.progress_bar.start(10)

        # 백그라운드 스레드에서 테스트 실행
        thread = threading.Thread(target=self._execute_test, args=(test_info,))
        thread.daemon = True
        thread.start()

    def _execute_test(self, test_info):
        """실제 테스트 실행 (백그라운드 스레드)"""

        try:
            # stdout/stderr 캡처 설정
            old_stdout = sys.stdout
            old_stderr = sys.stderr

            # 커스텀 출력 스트림
            class GuiOutputStream:
                def __init__(self, log_func, root):
                    self.log_func = log_func
                    self.root = root
                    self._buffer = ""
                    # TextIOWrapper 호환성을 위한 더미 속성
                    self.buffer = self  # 자기 자신을 buffer로 설정
                    self.encoding = 'utf-8'
                    self.errors = 'replace'

                def write(self, text):
                    self._buffer += text
                    if '\n' in self._buffer:
                        lines = self._buffer.split('\n')
                        for line in lines[:-1]:
                            if line.strip():
                                # 로그 레벨에 따라 색상 적용
                                if "✓" in line or "성공" in line or "PASS" in line:
                                    self.root.after(0, self.log_func, line, "success")
                                elif "✗" in line or "실패" in line or "FAIL" in line or "ERROR" in line:
                                    self.root.after(0, self.log_func, line, "error")
                                elif "⚠" in line or "경고" in line or "WARNING" in line:
                                    self.root.after(0, self.log_func, line, "warning")
                                elif "=" in line or "단계" in line or "[" in line:
                                    self.root.after(0, self.log_func, line, "header")
                                else:
                                    self.root.after(0, self.log_func, line)
                        self._buffer = lines[-1]

                def flush(self):
                    pass

                def readable(self):
                    return False

                def writable(self):
                    return True

                def seekable(self):
                    return False

                def isatty(self):
                    return False

                def fileno(self):
                    raise OSError("GuiOutputStream does not have a file descriptor")

                def close(self):
                    pass

                @property
                def closed(self):
                    return False

            gui_output = GuiOutputStream(self.log, self.root)
            sys.stdout = gui_output
            sys.stderr = gui_output

            # 테스트 모듈 import 및 실행
            self.log(f"▶ 테스트 실행 중...", "info")
            self.log("")

            # 동적 import
            import importlib
            module_name = test_info['module']

            try:
                test_module = importlib.import_module(module_name)
            except ImportError as e:
                self.log(f"✗ 모듈을 찾을 수 없습니다: {module_name}", "error")
                self.log(f"  오류: {e}", "error")
                self._finish_test(False)
                return

            # main() 함수 실행
            if not hasattr(test_module, 'main'):
                self.log(f"✗ {module_name}에 main() 함수가 없습니다", "error")
                self._finish_test(False)
                return

            # 테스트 실행
            try:
                test_module.main()
                success = True
            except Exception as e:
                self.log(f"\n✗ 테스트 실행 중 오류: {e}", "error")
                import traceback
                self.log(traceback.format_exc(), "error")
                success = False

            # 복원
            sys.stdout = old_stdout
            sys.stderr = old_stderr

            # 결과 출력
            self.root.after(0, self.log, "")
            if success:
                self.root.after(0, self.log, "="*60, "header")
                self.root.after(0, self.log, "✓ 테스트 완료 - 성공", "success")
                self.root.after(0, self.log, "="*60, "header")
            else:
                self.root.after(0, self.log, "="*60, "header")
                self.root.after(0, self.log, "✗ 테스트 완료 - 실패", "error")
                self.root.after(0, self.log, "="*60, "header")

            self._finish_test(success)

        except Exception as e:
            # 복원
            sys.stdout = old_stdout
            sys.stderr = old_stderr

            self.root.after(0, self.log, "")
            self.root.after(0, self.log, f"✗ 테스트 실행 중 오류 발생: {e}", "error")
            import traceback
            self.root.after(0, self.log, traceback.format_exc(), "error")
            self._finish_test(False)

    def _finish_test(self, success):
        """테스트 종료 처리"""

        self.is_running = False
        self.current_test = None
        self.progress_bar.stop()
        self.stop_btn.config(state=tk.DISABLED)

        if success:
            self.update_status("완료 - 성공 ✓")
        else:
            self.update_status("완료 - 실패 ✗")

    def stop_test(self):
        """테스트 중지"""
        if self.is_running:
            self.is_running = False
            self.log("\n⏹ 테스트 중지 요청...", "warning")

    def open_display_settings(self):
        """디스플레이 설정 다이얼로그 열기"""
        if self.is_running:
            messagebox.showwarning(
                "테스트 실행 중",
                "테스트가 실행 중일 때는 해상도를 변경할 수 없습니다."
            )
            return

        # 설정 다이얼로그 창
        dialog = tk.Toplevel(self.root)
        dialog.title("디스플레이 설정")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()

        # 센터에 배치
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (400 // 2)
        dialog.geometry(f"500x400+{x}+{y}")

        # 다이얼로그 내용
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 타이틀
        title = ttk.Label(
            main_frame,
            text="디스플레이 해상도 설정",
            font=("TkDefaultFont", 14, "bold")
        )
        title.pack(pady=(0, 10))

        # 설명
        desc = ttk.Label(
            main_frame,
            text="게임을 실행하는 디스플레이의 해상도를 선택하세요.\n"
                 "해상도에 맞는 템플릿 이미지가 사용됩니다.",
            font=("TkDefaultFont", 9),
            foreground="gray"
        )
        desc.pack(pady=(0, 20))

        # 현재 설정
        current_label = ttk.Label(
            main_frame,
            text=f"현재 설정: {self.current_resolution}",
            font=("TkDefaultFont", 10, "bold"),
            foreground="#2196F3"
        )
        current_label.pack(pady=(0, 20))

        # 해상도 선택 라디오 버튼
        resolution_var = tk.StringVar(value=self.current_resolution)

        radio_frame = ttk.LabelFrame(main_frame, text="해상도 선택", padding="15")
        radio_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        for res_key, res_info in SUPPORTED_RESOLUTIONS.items():
            # 템플릿 디렉토리 존재 확인
            res_dir = get_resolution_dir(res_key)
            template_exists = res_dir.exists()

            radio = ttk.Radiobutton(
                radio_frame,
                text=res_info['name'],
                value=res_key,
                variable=resolution_var
            )
            radio.pack(anchor=tk.W, pady=5)

            # 템플릿 상태 표시
            if template_exists:
                status_label = ttk.Label(
                    radio_frame,
                    text=f"  ✓ 템플릿 준비됨: {res_dir}",
                    font=("TkDefaultFont", 8),
                    foreground="green"
                )
            else:
                status_label = ttk.Label(
                    radio_frame,
                    text=f"  ✗ 템플릿 없음: {res_dir}",
                    font=("TkDefaultFont", 8),
                    foreground="red"
                )
            status_label.pack(anchor=tk.W, padx=(30, 0))

        # 버튼 프레임
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        def save_and_close():
            """설정 저장 및 닫기"""
            new_resolution = resolution_var.get()

            # 템플릿 디렉토리 확인
            new_res_dir = get_resolution_dir(new_resolution)
            if not new_res_dir.exists():
                result = messagebox.askyesno(
                    "템플릿 없음",
                    f"선택한 해상도({new_resolution})의 템플릿 디렉토리가 없습니다.\n\n"
                    f"디렉토리: {new_res_dir}\n\n"
                    f"그래도 변경하시겠습니까?\n"
                    f"(템플릿을 직접 추가해야 합니다)"
                )
                if not result:
                    return

            # 설정 저장
            save_display_settings(new_resolution)
            self.current_resolution = new_resolution
            self.display_btn.config(text=f"🖥 디스플레이: {new_resolution}")

            self.log(f"✓ 디스플레이 해상도 변경: {new_resolution}", "success")
            self.log(f"  템플릿 디렉토리: {new_res_dir}", "info")

            messagebox.showinfo(
                "설정 저장됨",
                f"디스플레이 해상도가 {new_resolution}로 변경되었습니다.\n\n"
                f"프로그램을 재시작하면 새 설정이 적용됩니다."
            )

            dialog.destroy()

        # 저장 버튼
        save_btn = tk.Button(
            button_frame,
            text="저장",
            command=save_and_close,
            bg="#4CAF50",
            fg="white",
            font=("TkDefaultFont", 10, "bold"),
            cursor="hand2",
            width=10
        )
        save_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 취소 버튼
        cancel_btn = tk.Button(
            button_frame,
            text="취소",
            command=dialog.destroy,
            bg="#757575",
            fg="white",
            font=("TkDefaultFont", 10, "bold"),
            cursor="hand2",
            width=10
        )
        cancel_btn.pack(side=tk.LEFT)


def main():
    """메인 함수"""
    try:
        root = tk.Tk()
        print("Tk 생성 완료")

        app = TestRunnerGUI(root)
        print("TestRunnerGUI 생성 완료")

        # 초기 메시지
        app.log("블루 아카이브 자동화 테스트 실행기가 시작되었습니다.", "info")
        app.log("왼쪽에서 실행할 테스트를 선택하세요.", "info")
        app.log("")
        app.log("⚠ 주의사항:", "warning")
        app.log("  1. 게임이 실행되어 있어야 합니다.", "warning")
        app.log("  2. 게임 화면이 보이는 상태여야 합니다.", "warning")
        app.log("  3. 테스트 시작 전 해당 화면으로 이동해주세요.", "warning")
        app.log("")

        root.mainloop()
    except Exception as e:
        print(f"GUI 실행 오류: {e}")
        import traceback
        traceback.print_exc()
        input("엔터를 눌러 종료...")


if __name__ == "__main__":
    main()
