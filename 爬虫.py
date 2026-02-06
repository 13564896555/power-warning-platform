import requests
import re
import json

url = 'https://www.weather.com.cn/weather/101220101.shtml'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

res = requests.get(url, headers=headers)
res.encoding = 'utf-8'
html = res.text

pattern = r'var observe24h_data = (\{.*?\});'
match = re.search(pattern, html, re.S)

if match:
    json_text = match.group(1)
    data = json.loads(json_text)

    latest = data['od']['od2'][0]
    hour = latest['od21']  # 小时
    temp = latest['od22']  # 温度
    wind = latest['od25']  # 风力
    humidity = latest['od27']  # 湿度

    print("最新一条天气信息：")
    print(f"小时: {hour}")
    print(f"温度: {temp}℃")
    print(f"风力: {wind}")
    print(f"湿度: {humidity}%")

else:
    print("没有找到 observe24h_data")
