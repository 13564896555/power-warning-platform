import pandas as pd
import numpy as np
import geopandas as gpd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure



def run_analysis(predict_func, title_name, frame):

    for widget in frame.winfo_children():
        widget.destroy()

    df = pd.read_csv("data.csv")

    A = df["a"]
    B = df["b"]
    C = df["c"]

    groups = [f"第{i+1}组" for i in range(len(df))]
    x = np.arange(len(groups))
    width = 0.25

    line = [predict_func(a, b, c) for a, b, c in zip(A, B, C)]


    fig = Figure(figsize=(10, 6), dpi=100)

    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)

    ax1.bar(x - width, A, width, label="A")
    ax1.bar(x, B, width, label="B")
    ax1.bar(x + width, C, width, label="C")

    ax1.plot(x, line, marker="o", linewidth=2, label=title_name)

    ax1.set_xticks(x)
    ax1.set_xticklabels(groups, rotation=45)
    ax1.set_title(title_name)
    ax1.legend()

    df2 = pd.read_excel("安徽省数值.xlsx")
    df2[title_name] = line
    df2.to_excel("安徽省数值_更新后.xlsx", index=False)

    Map = gpd.read_file('安徽省.shp')
    Data = pd.read_excel('安徽省数值_更新后.xlsx')

    Map['shi'] = Map['shi'].astype(str)
    Data['shi'] = Data['shi'].astype(str)

    Data_with_Map = pd.merge(Map, Data, on='shi', how='left')

    Data_with_Map.plot(
        column=title_name,
        cmap='OrRd',
        legend=True,
        ax=ax2
    )

    ax2.set_title(title_name + " 地图")


    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)True)


