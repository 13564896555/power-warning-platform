import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

df = pd.read_csv("data.csv")

def calculate(a, b, c):
    return a * 2 + b * 3 - c

results = []
labels = []

for i, row in df.iterrows():
    value = calculate(row["a"], row["b"], row["c"])
    results.append(value)
    labels.append(f"第{i+1}组")

plt.bar(labels, results)

plt.title("基于外部数据的计算结果柱状图")
plt.xlabel("数据组")
plt.ylabel("计算结果")

plt.show()

