import pandas as pd

df = pd.read_csv("source.csv", encoding="utf-8")
df.to_csv("data.csv", index=False, encoding="utf-8")
print("data.csv 创建成功")
