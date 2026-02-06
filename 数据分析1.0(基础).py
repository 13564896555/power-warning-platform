import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

df = pd.read_csv("data.csv")

A = df["a"]
B = df["b"]
C = df["c"]

groups = [f"第{i+1}组" for i in range(len(df))]
x = np.arange(len(groups))
width = 0.25

def predict1(a, b, c):
    return a * 2 + b * 3 - c

def predict2(a, b, c):
    return a + b + c

line1 = [predict1(a, b, c) for a, b, c in zip(A, B, C)]
line2 = [predict2(a, b, c) for a, b, c in zip(A, B, C)]

plt.bar(x - width, A, width, label="A")
plt.bar(x, B, width, label="B")
plt.bar(x + width, C, width, label="C")

plt.plot(x, line1, marker="o", color="black", linewidth=2, label="预测1")
plt.plot(x, line2, marker="s", color="red", linewidth=2, label="预测2")

plt.xticks(x, groups)
plt.xlabel("数据组")
plt.ylabel("数值")
plt.title("预警可视化")
plt.legend()
plt.grid(axis="y", linestyle="--", alpha=0.5)

plt.show()
