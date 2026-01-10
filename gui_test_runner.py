"""블루 아카이브 자동화 테스트 GUI

tkinter 기반 테스트 실행 및 모니터링 GUI
체크박스 기반 선택 실행 시스템
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

        self.root.geometry("1300x750")

        # 테스트 실행 상태
        self.is_running = False
        self.current_test = None
        self.test_results = {}  # {module: "PASS"|"FAIL"|"BLOCKED"}

        # 현재 해상도 설정
        self.current_resolution = CURRENT_RESOLUTION

        # 체크박스 변수 저장
        self.test_vars = {}
        self.test_items = []

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


        # 왼쪽 패널: 테스트 항목 체크박스
        left_frame = ttk.LabelFrame(main_frame, text="테스트 선택", padding="10")
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))

        # 오른쪽 패널: 로그 출력
        right_frame = ttk.LabelFrame(main_frame, text="실시간 로그", padding="10")
        right_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)

        # 테스트 항목 체크박스 생성
        self.create_test_checkboxes(left_frame)

        # 로그 출력 창
        self.create_log_panel(right_frame)

        # 하단 상태바
        self.create_status_bar(main_frame)

    def create_test_checkboxes(self, parent):
        """테스트 항목 체크박스 생성"""

        # 테스트 목록 정의 (의존성 포함)
        tests = [
            {
                "id": "TC-001",
                "name": "기본 모듈 테스트",
                "description": "TemplateMatcher, GameController 등 기본 모듈 동작 확인",
                "module": "tests.test_modules",
                "color": "#4CAF50",
                "dependencies": []  # 의존성 없음
            },
            {
                "id": "TC-002",
                "name": "단계 1-2.5: 스테이지 진입",
                "description": "시작 발판 → 편성 → 출격 → 맵 → 임무 개시",
                "module": "tests.test_partial_stage",
                "color": "#2196F3",
                "dependencies": []
            },
            {
                "id": "TC-003",
                "name": "단계 3: 발판 이동 및 전투 진입",
                "description": "적 발판/빈 발판 클릭 및 이동 테스트",
                "module": "tests.test_tile_movement",
                "color": "#FF9800",
                "dependencies": []  # TC-002 필요
            },
            {
                "id": "TC-004",
                "name": "단계 4: 학생 별 스킬 확인",
                "description": "학생 별 ex 스킬 사용 확인",
                "module": "tests.test_skill_usage_v2",
                "color": "#00FDB1",
                "dependencies": []  # TC-003 필요
            },
            {
                "id": "TC-006",
                "name": "단계 6: 전투 결과 확인",
                "description": "전투 결과 → 통계 → 데미지 기록 → 랭크 획득",
                "module": "tests.test_battle_result",
                "color": "#9C27B0",
                "dependencies": []  # 전투 진입 해야함
            },
            {
                "id": "TC-007",
                "name": "보상 획득 UI 검증",
                "description": "Victory → MISSION COMPLETE → 보상 아이템 UI 확인",
                "module": "tests.test_reward_ui_verification",
                "color": "#FF5722",
                "dependencies": []  # Victory 화면에서 시작
            },
        ]

        self.test_items = tests

        # 스크롤 가능한 프레임
        canvas = tk.Canvas(parent, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # 체크박스 생성
        for idx, test in enumerate(tests):
            # 체크박스 프레임
            test_frame = ttk.Frame(scrollable_frame, relief=tk.RIDGE, borderwidth=1)
            test_frame.grid(row=idx, column=0, pady=5, padx=5, sticky=(tk.W, tk.E))

            # 체크박스 변수
            var = tk.BooleanVar(value=False)
            self.test_vars[test['module']] = var

            # 상태 레이블 (Ready/Running/Pass/Fail/Blocked)
            status_label = ttk.Label(
                test_frame,
                text="●",
                font=("TkDefaultFont", 12),
                foreground="gray",
                width=2
            )
            status_label.grid(row=0, column=0, padx=(5, 0))
            test['status_label'] = status_label

            # 체크박스
            cb = ttk.Checkbutton(
                test_frame,
                text=f"{test['id']}: {test['name']}",
                variable=var,
                command=lambda: self.update_dependencies()
            )
            cb.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

            # 설명 레이블
            desc_label = ttk.Label(
                test_frame,
                text=test["description"],
                font=("TkDefaultFont", 8),
                foreground="gray"
            )
            desc_label.grid(row=1, column=1, sticky=tk.W, padx=5, pady=(0, 5))

            # 의존성 표시
            if test['dependencies']:
                dep_text = "의존성: " + ", ".join([self._get_test_id_by_module(dep) for dep in test['dependencies']])
                dep_label = ttk.Label(
                    test_frame,
                    text=dep_text,
                    font=("TkDefaultFont", 7),
                    foreground="#FF5722"
                )
                dep_label.grid(row=2, column=1, sticky=tk.W, padx=5, pady=(0, 5))

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 하단 버튼 프레임
        button_frame = ttk.Frame(parent)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))

        # 전체 선택/해제 버튼
        select_all_btn = tk.Button(
            button_frame,
            text="전체 선택",
            command=self.select_all,
            bg="#2196F3",
            fg="white",
            font=("TkDefaultFont", 9),
            cursor="hand2"
        )
        select_all_btn.pack(side=tk.LEFT, padx=2)

        deselect_all_btn = tk.Button(
            button_frame,
            text="전체 해제",
            command=self.deselect_all,
            bg="#607D8B",
            fg="white",
            font=("TkDefaultFont", 9),
            cursor="hand2"
        )
        deselect_all_btn.pack(side=tk.LEFT, padx=2)

        # 선택 항목 실행 버튼
        run_selected_btn = tk.Button(
            button_frame,
            text="▶ 선택 항목 실행",
            command=self.run_selected_tests,
            bg="#4CAF50",
            fg="white",
            font=("TkDefaultFont", 10, "bold"),
            cursor="hand2",
            height=2
        )
        run_selected_btn.pack(side=tk.RIGHT, padx=2, fill=tk.X, expand=True)
        self.run_selected_btn = run_selected_btn

        # 중지 버튼
        stop_btn = tk.Button(
            button_frame,
            text="⏹ 중지",
            command=self.stop_test,
            bg="#F44336",
            fg="white",
            font=("TkDefaultFont", 10, "bold"),
            cursor="hand2",
            state=tk.DISABLED,
            height=2
        )
        stop_btn.pack(side=tk.RIGHT, padx=2)
        self.stop_btn = stop_btn

    def _get_test_id_by_module(self, module):
        """모듈명으로 테스트 ID 찾기"""
        for test in self.test_items:
            if test['module'] == module:
                return test['id']
        return module

    def select_all(self):
        """모든 테스트 선택"""
        for var in self.test_vars.values():
            var.set(True)
        self.update_dependencies()

    def deselect_all(self):
        """모든 테스트 해제"""
        for var in self.test_vars.values():
            var.set(False)
        self.update_dependencies()

    def update_dependencies(self):
        """의존성 체크 및 Block 상태 업데이트"""
        # 현재 선택된 테스트
        selected = [test['module'] for test in self.test_items if self.test_vars[test['module']].get()]

        for test in self.test_items:
            # 의존성 체크
            if test['dependencies']:
                deps_satisfied = all(
                    self.test_results.get(dep) == "PASS" for dep in test['dependencies']
                )

                if not deps_satisfied and test['module'] in selected:
                    # 의존성 미충족이지만 선택된 경우
                    missing_deps = [
                        self._get_test_id_by_module(dep)
                        for dep in test['dependencies']
                        if self.test_results.get(dep) != "PASS"
                    ]
                    # 체크 해제하지 않고 경고만 표시 (실행 시 Block 처리)

    def run_selected_tests(self):
        """선택된 테스트 순차 실행"""
        if self.is_running:
            self.log("⚠ 테스트가 이미 실행 중입니다.", "warning")
            return

        # 선택된 테스트 필터링
        selected_tests = [test for test in self.test_items if self.test_vars[test['module']].get()]

        if not selected_tests:
            messagebox.showwarning("선택 없음", "실행할 테스트를 선택해주세요.")
            return

        self.log(f"✓ {len(selected_tests)}개 테스트 선택됨", "success")
        self.log("")

        # 백그라운드 스레드에서 순차 실행
        thread = threading.Thread(target=self._run_tests_sequentially, args=(selected_tests,))
        thread.daemon = True
        thread.start()

    def _run_tests_sequentially(self, tests):
        """선택된 테스트를 순차적으로 실행"""
        self.is_running = True
        self.root.after(0, lambda: self.run_selected_btn.config(state=tk.DISABLED))
        self.root.after(0, lambda: self.stop_btn.config(state=tk.NORMAL))
        self.root.after(0, self.progress_bar.start, 10)

        for idx, test in enumerate(tests):
            if not self.is_running:
                self.root.after(0, self.log, "\n⏹ 사용자가 테스트를 중지했습니다.", "warning")
                break

            self.root.after(0, self.log, f"\n{'='*60}", "header")
            self.root.after(0, self.log, f"[{idx+1}/{len(tests)}] {test['id']}: {test['name']}", "header")
            self.root.after(0, self.log, f"{'='*60}", "header")

            # 의존성 체크
            if test['dependencies']:
                deps_satisfied = all(
                    self.test_results.get(dep) == "PASS" for dep in test['dependencies']
                )

                if not deps_satisfied:
                    missing_deps = [
                        self._get_test_id_by_module(dep)
                        for dep in test['dependencies']
                        if self.test_results.get(dep) != "PASS"
                    ]
                    self.root.after(0, self.log, f"⚠ 의존성 미충족: {', '.join(missing_deps)}", "warning")
                    self.root.after(0, self.log, "✗ 테스트 건너뜀 (BLOCKED)", "error")
                    self.test_results[test['module']] = "BLOCKED"
                    self.root.after(0, self._update_status_label, test, "BLOCKED")
                    continue

            # 상태 업데이트: Running
            self.root.after(0, self._update_status_label, test, "RUNNING")

            # 테스트 실행
            success = self._execute_single_test(test)

            # 결과 저장 및 상태 업데이트
            if success:
                self.test_results[test['module']] = "PASS"
                self.root.after(0, self._update_status_label, test, "PASS")
            else:
                self.test_results[test['module']] = "FAIL"
                self.root.after(0, self._update_status_label, test, "FAIL")

        # 종료 처리
        self.root.after(0, self._finish_all_tests, tests)

    def _execute_single_test(self, test_info):
        """단일 테스트 실행"""
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
                    self.buffer = self
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
            self.root.after(0, self.log, f"▶ 테스트 실행 중...", "info")
            self.root.after(0, self.log, "")

            # 동적 import
            import importlib
            module_name = test_info['module']

            try:
                test_module = importlib.import_module(module_name)
            except ImportError as e:
                self.root.after(0, self.log, f"✗ 모듈을 찾을 수 없습니다: {module_name}", "error")
                self.root.after(0, self.log, f"  오류: {e}", "error")
                sys.stdout = old_stdout
                sys.stderr = old_stderr
                return False

            # main() 함수 실행
            if not hasattr(test_module, 'main'):
                self.root.after(0, self.log, f"✗ {module_name}에 main() 함수가 없습니다", "error")
                sys.stdout = old_stdout
                sys.stderr = old_stderr
                return False

            # 테스트 실행
            try:
                test_module.main()
                success = True
            except Exception as e:
                self.root.after(0, self.log, f"\n✗ 테스트 실행 중 오류: {e}", "error")
                import traceback
                self.root.after(0, self.log, traceback.format_exc(), "error")
                success = False

            # 복원
            sys.stdout = old_stdout
            sys.stderr = old_stderr

            return success

        except Exception as e:
            # 복원
            sys.stdout = old_stdout
            sys.stderr = old_stderr

            self.root.after(0, self.log, "")
            self.root.after(0, self.log, f"✗ 테스트 실행 중 오류 발생: {e}", "error")
            import traceback
            self.root.after(0, self.log, traceback.format_exc(), "error")
            return False

    def _update_status_label(self, test, status):
        """테스트 상태 레이블 업데이트"""
        label = test['status_label']
        if status == "READY":
            label.config(text="●", foreground="gray")
        elif status == "RUNNING":
            label.config(text="▶", foreground="blue")
        elif status == "PASS":
            label.config(text="✓", foreground="green")
        elif status == "FAIL":
            label.config(text="✗", foreground="red")
        elif status == "BLOCKED":
            label.config(text="⊗", foreground="orange")

    def _finish_all_tests(self, tests):
        """전체 테스트 완료 처리"""
        self.is_running = False
        self.progress_bar.stop()
        self.run_selected_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)



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

    def stop_test(self):
        """테스트 중지"""
        if self.is_running:
            self.is_running = False
            self.log("\n⏹ 테스트 중지 요청...", "warning")


def main():
    """메인 함수"""
    try:
        root = tk.Tk()
        print("Tk 생성 완료")

        app = TestRunnerGUI(root)
        print("TestRunnerGUI 생성 완료")

        # 초기 메시지
        app.log("블루 아카이브 자동화 테스트 실행기가 시작되었습니다.", "info")
        app.log("왼쪽에서 실행할 테스트를 선택하고 '선택 항목 실행' 버튼을 클릭하세요.", "info")
        app.log("")
        app.log("⚠ 주의사항:", "warning")
        app.log("  1. 게임이 실행되어 있어야 합니다.", "warning")
        app.log("  2. 게임 화면이 보이는 상태여야 합니다.", "warning")
        app.log("  3. 테스트 시작 전 해당 화면으로 이동해주세요.", "warning")
        app.log("  4. 의존성이 있는 테스트는 선행 테스트 성공 필요합니다.", "warning")
        app.log("")

        root.mainloop()
    except Exception as e:
        print(f"GUI 실행 오류: {e}")
        import traceback
        traceback.print_exc()
        input("엔터를 눌러 종료...")


if __name__ == "__main__":
    main()
