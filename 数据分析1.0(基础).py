import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False


data = [
    (1, 2, 3),
    (2, 3, 1),
    (3, 1, 2),
    (4, 2, 1),
    (2, 4, 3),
    (3, 3, 2),
    (5, 1, 4),
    (4, 3, 2)
]

def calculate(a, b, c):
    return a * 2 + b * 3 - c


results = []
labels = []

for i, (a, b, c) in enumerate(data, start=1):
    value = calculate(a, b, c)
    results.append(value)
    labels.append(f"第{i}组")

plt.bar(labels, results)

plt.title("8 组数据计算结果柱状图")
plt.xlabel("数据组")
plt.ylabel("计算结果")

plt.show()
