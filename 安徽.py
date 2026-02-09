# 库的导入
import pandas as pd                 # 数据信息处理
import geopandas as gpd             # 地理信息处理
import matplotlib.pyplot as plt     # 可视化处理



Map = gpd.read_file('C:/Users/fytz6/Desktop/安徽省/安徽省.shp')

Data = pd.read_excel('C:/Users/fytz6/Desktop/安徽省数值.xlsx')    # 导入数据


# 将Map与Data匹配
# 左表
Map['shi'] = Map['shi'].astype(str)

# 右表
Data['shi'] = Data['shi'].astype(str)

Data_with_Map = pd.merge(left=Map, right=Data, how='left',
                         left_on='shi', right_on='shi')

Data_with_Map.plot(column='数值',
                   cmap='OrRd',  # 设置色阶样式
                   legend=True,  # 显示色阶
                   missing_kwds={
                       "color": "grey",
                       "edgecolor": "black",
                       "hatch": ".",
                       "alpha": 0.2
                   })


plt.show()