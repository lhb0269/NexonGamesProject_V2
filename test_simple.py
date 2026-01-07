"""간단한 GUI 테스트"""
import tkinter as tk

print("프로그램 시작")

root = tk.Tk()
root.title("테스트")
root.geometry("300x200")

label = tk.Label(root, text="GUI 테스트 성공!", font=("맑은 고딕", 16))
label.pack(pady=50)

print("GUI 생성 완료")

root.mainloop()
