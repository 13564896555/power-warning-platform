import requests
import json
import re
urls = [
    "https://d1.weather.com.cn/sk_2d/101220101.html?_=1770886030438",  # 合肥
    "https://d1.weather.com.cn/sk_2d/101220201.html?_=1770884680956",  # 蚌埠
    "https://d1.weather.com.cn/sk_2d/101220301.html?_=1770886155252",  # 芜湖
    "https://d1.weather.com.cn/sk_2d/101220401.html?_=1770886239258",  # 淮南
    "https://d1.weather.com.cn/sk_2d/101220501.html?_=1770886298756",  # 马鞍山
    "https://d1.weather.com.cn/sk_2d/101221201.html?_=1770886443435",  # 淮北
    "https://d1.weather.com.cn/sk_2d/101221301.html?_=1770886498858",  # 铜陵
    "https://d1.weather.com.cn/sk_2d/101220601.html?_=1770886539638",  # 安庆
    "https://d1.weather.com.cn/sk_2d/101221001.html?_=1770886577376",  # 黄山
    "https://d1.weather.com.cn/sk_2d/101221101.html?_=1770886656299",  # 滁州
    "https://d1.weather.com.cn/sk_2d/101220801.html?_=1770886695127",  # 阜阳
    "https://d1.weather.com.cn/sk_2d/101220701.html?_=1770886748695",  # 宿州
    "https://d1.weather.com.cn/sk_2d/101221501.html?_=1770886776481",  # 六安
    "https://d1.weather.com.cn/sk_2d/101220901.html?_=1770886817036",  # 亳州
    "https://d1.weather.com.cn/sk_2d/101221701.html?_=1770886886566",  # 池州
    "https://d1.weather.com.cn/sk_2d/101221401.html?_=1770886928494"   # 宣城
]

headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "http://www.weather.com.cn/"
}

for url in urls:

    response = requests.get(url, headers=headers)
    response.encoding = "utf-8"

    text = response.text

    match = re.search(r'var dataSK\s*=\s*(\{.*?\})', text)

    if match:
        json_str = match.group(1)
        data = json.loads(json_str)

        print("城市:", data["cityname"])
        print("温度:", data["temp"])
        print("风速:", data["wse"])
        print("湿度:", data["SD"])
    else:
        print("没有匹配到数据")
