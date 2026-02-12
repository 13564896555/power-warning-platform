import tkinter as tk
import analysis
import matplotlib
matplotlib.rcParams["font.sans-serif"] = ["SimHei"]
matplotlib.rcParams["axes.unicode_minus"] = False

def predict1(a, b, c):
    return a+b*3-c


def predict2(a, b, c):
    return a+b-c


def predict3(a, b, c):
    return a+2*b-c


root = tk.Tk()
root.title("安徽省预警分析系统")
root.geometry("1100x700")
root.configure(bg="#f2f2f2")

btn_frame = tk.Frame(root, bg="#f2f2f2")
btn_frame.pack(side="top", fill="x", pady=15)


chart_frame = tk.Frame(root, bg="white")
chart_frame.pack(side="top", fill="both", expand=True, padx=20, pady=10)

def create_button(text, func):
    return tk.Button(
        btn_frame,
        text=text,
        command=func,
        font=("微软雅黑", 12),
        width=15,
        height=2,
        bg="#2d89ef",
        fg="white",
        activebackground="#1b5fad",
        relief="flat"
    )

create_button(
    "模型一",
    lambda: analysis.run_analysis(predict1, "预测1", chart_frame)
).pack(side="left", padx=20)

create_button(
    "模型二",
    lambda: analysis.run_analysis(predict2, "预测2", chart_frame)
).pack(side="left", padx=20)

create_button(
    "模型三",
    lambda: analysis.run_analysis(predict3, "预测3", chart_frame)
).pack(side="left", padx=20)


root.mainloop()
