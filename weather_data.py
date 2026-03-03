import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
from functools import lru_cache
from config import WEATHER_API_KEY

class WeatherDataGenerator:
    """
    天气数据生成器
    模拟安徽省的天气状况，包括温度、湿度、风速、日照时长等
    支持通过和风天气API获取真实天气数据
    """
    
    def __init__(self):
        # 和风天气API设置
        self.api_key = WEATHER_API_KEY
        self.base_url = "https://nq2tuphf9j.re.qweatherapi.com/v7/"
        
        # 安徽省市级行政区城市ID
        self.cities = {
        "合肥市": "101220101",
        "芜湖市": "101220201",
        "蚌埠市": "101220301",
        "淮南市": "101220401",
        "马鞍山市": "101220501",
        "淮北市": "101220601",
        "铜陵市": "101220701",
        "安庆市": "101220801",
        "黄山市": "101220901",
        "滁州市": "101221001",
        "阜阳市": "101221101",
        "宿州市": "101221201",
        "六安市": "101221301",
        "亳州市": "101221401",
        "池州市": "101221501",
        "宣城市": "101221601"}
        
        # 基础参数设置
        self.base_temperature = 20  # 基础温度 (℃)
        self.base_humidity = 60     # 基础湿度 (%)
        self.base_wind_speed = 5    # 基础风速 (m/s)
        self.base_sunshine_hours = 8  # 基础日照时长 (小时)
        
        # 波动参数
        self.temperature_variation = 5  # 温度波动
        self.humidity_variation = 15    # 湿度波动
        self.wind_speed_variation = 3   # 风速波动
        self.sunshine_hours_variation = 3  # 日照时长波动
        
        # 时间相关参数
        # 24小时温度变化正弦曲线：0 点最低，12 点最高，振幅 1
        self.hourly_temp_pattern = np.sin(np.linspace(0, 2 * np.pi, 24))
    
    def generate_historical_data(self, hours=1, city=None):
        """
        生成历史天气数据
        
        参数:
        hours: 生成数据的小时数
        city: 城市名称,None表示所有城市
        
        返回:
        包含历史天气数据的DataFrame
        """
        # 生成时间序列
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)  # 计算历史数据的起始时间
        # 生成以3分钟为间隔的时间序列，用于后续逐分钟模拟天气数据
        time_index = pd.date_range(start=start_time, end=end_time, freq='3T')
        
        # 生成天气数据
        data = []
        
        # 确定要处理的城市
        cities_to_process = [city] if city and city in self.cities else list(self.cities.keys())
        
        for city_name in cities_to_process:
            city_id = self.cities[city_name]
            
            # 首先获取实时天气数据作为基础
            real_time_data = self.generate_real_time_data(city=city_name)
            
            # 获取24小时预报数据，用于填充历史数据
            if self.api_key:
                try:
                    print(f"正在调用和风天气API获取{city_name}24小时预报数据...")
                    # 获取24小时预报数据
                    hourly_url = f"{self.base_url}weather/24h?location={city_id}&key={self.api_key}"
                    
                    # 添加请求头模拟浏览器请求
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                        'Referer': 'https://www.qweather.com/',
                        'Accept': 'application/json, text/plain, */*',
                        'Accept-Language': 'zh-CN,zh;q=0.9',
                        'Accept-Encoding': 'gzip, deflate, br'
                    }
                    
                    hourly_response = requests.get(hourly_url, headers=headers)
                    hourly_data = hourly_response.json()
                    
                    if hourly_data.get('code') == '200':
                        hourly_forecast = hourly_data.get('hourly', [])
                        print(f"获取到 {len(hourly_forecast)} 小时的天气预报数据")
                        
                        # 处理每小时的预报数据
                        for item in hourly_forecast:
                            timestamp = pd.to_datetime(item.get('fxTime', datetime.now()))
                            # 移除时区信息，使其与start_time和end_time格式一致
                            timestamp = timestamp.replace(tzinfo=None)
                            
                            # 只处理最近1小时的数据
                            if start_time <= timestamp <= end_time:
                                temperature = float(item.get('temp', 20))
                                humidity = float(item.get('humidity', 60))
                                wind_speed = float(item.get('windSpeed', 5))
                                weather_condition = item.get('text', '晴天')
                                
                                # 计算日照时长
                                hour = timestamp.hour
                                sunshine_hours = 0
                                if 6 <= hour <= 18:
                                    # 尝试获取当天的日照时长
                                    try:
                                        daily_url = f"{self.base_url}weather/7d?location={city_id}&key={self.api_key}"
                                        daily_response = requests.get(daily_url, headers=headers)
                                        daily_data = daily_response.json()
                                        if daily_data.get('code') == '200':
                                            date_str = timestamp.strftime('%Y-%m-%d')
                                            for day in daily_data.get('daily', []):
                                                if day.get('date') == date_str:
                                                    sunshine_hours = float(day.get('sunshine', 8)) / 13  # 平均到每小时
                                                    break
                                    except:
                                        sunshine_hours = 8 / 13
                                
                                data.append({
                                    'city': city_name,
                                    'timestamp': timestamp,
                                    'temperature': temperature,
                                    'humidity': humidity,
                                    'wind_speed': wind_speed,
                                    'sunshine_hours': sunshine_hours,
                                    'weather_condition': weather_condition
                                })
                        
                        # 添加实时数据到历史数据中
                        for _, row in real_time_data.iterrows():
                            # 确保时间戳在范围内
                            timestamp = row['timestamp']
                            if start_time <= timestamp <= end_time:
                                # 检查该时间戳是否已经有数据
                                has_data = any(item['timestamp'] == timestamp and item['city'] == city_name for item in data)
                                if not has_data:
                                    data.append(row.to_dict())
                        
                        # 计算当前城市的数据量
                        city_data_count = len([item for item in data if item['city'] == city_name])
                        expected_count = len(time_index)
                        
                        # 如果数据不足，使用实时数据的参数来填充
                        if city_data_count < expected_count:
                            print(f"{city_name} 数据不足，使用实时数据参数填充")
                            # 使用实时数据的参数
                            if not real_time_data.empty:
                                real_time_row = real_time_data.iloc[0]
                                real_temp = real_time_row['temperature']
                                real_humidity = real_time_row['humidity']
                                real_wind = real_time_row['wind_speed']
                                real_sunshine = real_time_row['sunshine_hours']
                                real_weather = real_time_row['weather_condition']
                            else:
                                # 如果没有实时数据，使用默认值
                                real_temp = 20
                                real_humidity = 60
                                real_wind = 5
                                real_sunshine = 0
                                real_weather = '晴天'
                            
                            # 填充剩余的数据点
                            for timestamp in time_index:
                                # 检查该时间戳是否已经有数据
                                has_data = any(item['timestamp'] == timestamp and item['city'] == city_name for item in data)
                                if not has_data:
                                    # 使用实时数据的参数，添加一些小的随机波动
                                    hour = timestamp.hour
                                    temp_factor = self.hourly_temp_pattern[hour]
                                    temperature = real_temp + temp_factor * 2 + np.random.normal(0, 1)
                                    humidity = max(0, min(100, real_humidity + np.random.normal(0, 5)))
                                    wind_speed = max(0, real_wind + np.random.normal(0, 1))
                                    
                                    # 计算日照时长
                                    if 6 <= hour <= 18:
                                        sunshine_hours = real_sunshine
                                    else:
                                        sunshine_hours = 0
                                    
                                    data.append({
                                        'city': city_name,
                                        'timestamp': timestamp,
                                        'temperature': temperature,
                                        'humidity': humidity,
                                        'wind_speed': wind_speed,
                                        'sunshine_hours': sunshine_hours,
                                        'weather_condition': real_weather
                                    })
                        else:
                            print(f"{city_name} 成功获取所有历史天气数据")
                        
                        continue
                except Exception as e:
                    # 发生异常，使用实时数据填充
                    print(f"获取{city_name}历史天气数据失败: {e}")
                    print(f"使用实时数据填充{city_name}历史天气数据")
            
            # 使用实时数据填充
            if not real_time_data.empty:
                real_time_row = real_time_data.iloc[0]
                real_temp = real_time_row['temperature']
                real_humidity = real_time_row['humidity']
                real_wind = real_time_row['wind_speed']
                real_sunshine = real_time_row['sunshine_hours']
                real_weather = real_time_row['weather_condition']
            else:
                # 如果没有实时数据，使用默认值
                real_temp = 20
                real_humidity = 60
                real_wind = 5
                real_sunshine = 0
                real_weather = '晴天'
            
            # 生成历史数据
            for timestamp in time_index:
                # 检查该时间戳是否已经有数据
                has_data = any(item['timestamp'] == timestamp and item['city'] == city_name for item in data)
                if not has_data:
                    # 使用实时数据的参数，添加一些小的随机波动
                    hour = timestamp.hour
                    temp_factor = self.hourly_temp_pattern[hour]
                    temperature = real_temp + temp_factor * 2 + np.random.normal(0, 1)
                    humidity = max(0, min(100, real_humidity + np.random.normal(0, 5)))
                    wind_speed = max(0, real_wind + np.random.normal(0, 1))
                    
                    # 计算日照时长
                    if 6 <= hour <= 18:
                        sunshine_hours = real_sunshine
                    else:
                        sunshine_hours = 0
                    
                    data.append({
                        'city': city_name,
                        'timestamp': timestamp,
                        'temperature': temperature,
                        'humidity': humidity,
                        'wind_speed': wind_speed,
                        'sunshine_hours': sunshine_hours,
                        'weather_condition': real_weather
                    })
        
        return pd.DataFrame(data)
    
    def generate_real_time_data(self, city=None):
        """
        生成实时天气数据
        
        参数:
        city: 城市名称,None表示所有城市
        
        返回:
        包含实时天气数据的DataFrame
        """
        timestamp = datetime.now()
        data = []
        
        # 确定要处理的城市
        cities_to_process = [city] if city and city in self.cities else list(self.cities.keys())
        
        for city_name in cities_to_process:
            city_id = self.cities[city_name]
            
            # 如果提供了API密钥，通过和风天气API获取真实数据
            if self.api_key:
                try:
                    # 获取实时天气
                    print(f"正在调用和风天气API获取{city_name}实时天气数据...")
                    now_url = f"{self.base_url}weather/now?location={city_id}&key={self.api_key}"
                    
                    # 添加请求头模拟浏览器请求
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                        'Referer': 'https://www.qweather.com/',
                        'Accept': 'application/json, text/plain, */*',
                        'Accept-Language': 'zh-CN,zh;q=0.9',
                        'Accept-Encoding': 'gzip, deflate, br'
                    }
                    
                    response = requests.get(now_url, headers=headers)
                    data_json = response.json()
                    
                    if data_json.get('code') == '200':
                        now = data_json.get('now', {})
                        temperature = float(now.get('temp', 20))
                        humidity = float(now.get('humidity', 60))
                        wind_speed = float(now.get('windSpeed', 5))  # 使用正确的风速字段
                        
                        # 尝试获取日照时长
                        sunshine_hours = 0
                        hour = timestamp.hour
                        if 6 <= hour <= 18:
                            # 尝试通过7天历史接口获取当天的日照时长
                            try:
                                historical_url = f"{self.base_url}weather/7d?location={city_id}&key={self.api_key}"
                                historical_response = requests.get(historical_url, headers=headers)
                                historical_data = historical_response.json()
                                if historical_data.get('code') == '200':
                                    today = historical_data.get('daily', [])[0]
                                    sunshine_hours = float(today.get('sunshine', 8)) / 13  # 平均到每小时
                            except:
                                # 获取日照时长失败，使用默认值
                                sunshine_hours = 8 / 13
                        
                        weather_condition = now.get('text', '晴天')
                    else:
                        # API调用失败，使用模拟数据
                        simulated_data = self._generate_simulated_data(timestamp, city_name)
                        data.append(simulated_data.iloc[0].to_dict())
                        continue
                except Exception as e:
                    # 发生异常，使用模拟数据
                    print(f"获取{city_name}天气数据失败: {e}")
                    simulated_data = self._generate_simulated_data(timestamp, city_name)
                    data.append(simulated_data.iloc[0].to_dict())
                    continue
            else:
                # 没有提供API密钥，使用模拟数据
                simulated_data = self._generate_simulated_data(timestamp, city_name)
                data.append(simulated_data.iloc[0].to_dict())
                continue
            
            data.append({
                'city': city_name,
                'timestamp': timestamp,
                'temperature': temperature,
                'humidity': humidity,
                'wind_speed': wind_speed,
                'sunshine_hours': sunshine_hours,
                'weather_condition': weather_condition
            })
        
        return pd.DataFrame(data)
    
    def _generate_simulated_data(self, timestamp, city_name):
        """
        生成模拟天气数据
        
        参数:
        timestamp: 时间戳
        city_name: 城市名称
        
        返回:
        包含模拟天气数据的DataFrame
        """
        hour = timestamp.hour
        
        # 为每个城市添加一些随机差异
        city_factor = hash(city_name) % 10 / 10  # 0-1之间的城市因子
        
        # 计算温度
        temp_factor = self.hourly_temp_pattern[hour]
        temperature = self.base_temperature + city_factor * 2 + temp_factor * 5 + self.temperature_variation * np.random.normal()
        
        # 计算其他天气参数
        humidity = max(0, min(100, self.base_humidity + city_factor * 10 + self.humidity_variation * np.random.normal()))
        wind_speed = max(0, self.base_wind_speed + city_factor * 2 + self.wind_speed_variation * np.random.normal())
        
        # 计算日照时长
        if 6 <= hour <= 18:
            sunshine_hours = max(0, self.base_sunshine_hours + city_factor * 2 + self.sunshine_hours_variation * np.random.normal()) / 13
        else:
            sunshine_hours = 0
        
        # 计算天气状况
        weather_condition = self._get_weather_condition(temperature, humidity, wind_speed, sunshine_hours * 13)
        
        data = {
            'city': city_name,
            'timestamp': timestamp,
            'temperature': temperature,
            'humidity': humidity,
            'wind_speed': wind_speed,
            'sunshine_hours': sunshine_hours,
            'weather_condition': weather_condition
        }
        return pd.DataFrame([data])
    
    def generate_forecast_data(self, hours=24, city=None):
        """
        生成未来天气预测数据
        
        参数:
        hours: 预测小时数
        city: 城市名称,None表示所有城市
        
        返回:
        包含预测天气数据的DataFrame
        """
        # 生成时间序列
        start_time = datetime.now()
        time_index = pd.date_range(start=start_time, periods=hours*20, freq='3T')
        
        # 生成预测数据
        data = []
        
        # 确定要处理的城市
        cities_to_process = [city] if city and city in self.cities else list(self.cities.keys())
        
        for city_name in cities_to_process:
            city_id = self.cities[city_name]
            
            # 如果提供了API密钥，通过和风天气API获取真实数据
            if self.api_key and hours <= 24:
                try:
                    # 获取24小时天气预报
                    print(f"正在调用和风天气API获取{city_name}24小时天气预报...")
                    hourly_url = f"{self.base_url}weather/24h?location={city_id}&key={self.api_key}"
                    
                    # 添加请求头模拟浏览器请求
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                        'Referer': 'https://www.qweather.com/',
                        'Accept': 'application/json, text/plain, */*',
                        'Accept-Language': 'zh-CN,zh;q=0.9',
                        'Accept-Encoding': 'gzip, deflate, br'
                    }
                    
                    response = requests.get(hourly_url, headers=headers)
                    forecast_data = response.json()
                    
                    if forecast_data.get('code') == '200':
                        hourly_forecast = forecast_data.get('hourly', [])
                        print(f"获取到 {len(hourly_forecast)} 小时的天气预报数据")
                        
                        # 尝试获取7天预报以获取日照时长
                        sunshine_data = {}
                        try:
                            daily_url = f"{self.base_url}weather/7d?location={city_id}&key={self.api_key}"
                            daily_response = requests.get(daily_url, headers=headers)
                            daily_data = daily_response.json()
                            if daily_data.get('code') == '200':
                                for day in daily_data.get('daily', []):
                                    date_str = day.get('date', '')
                                    if date_str:
                                        sunshine_data[date_str] = float(day.get('sunshine', 8))
                        except:
                            pass
                        
                        # 处理每小时的预测数据
                        for i, item in enumerate(hourly_forecast):
                            if i >= hours:
                                break
                            
                            timestamp = pd.to_datetime(item.get('fxTime', start_time))
                            temperature = float(item.get('temp', 20))
                            humidity = float(item.get('humidity', 60))
                            wind_speed = float(item.get('windSpeed', 5))  # 使用正确的风速字段
                            
                            # 计算日照时长
                            hour = timestamp.hour
                            sunshine_hours = 0
                            if 6 <= hour <= 18:
                                # 从7天预报中获取当天的日照时长
                                date_str = timestamp.strftime('%Y-%m-%d')
                                day_sunshine = sunshine_data.get(date_str, 8)
                                sunshine_hours = day_sunshine / 13  # 平均到每小时
                            
                            weather_condition = item.get('text', '晴天')
                            
                            data.append({
                                'city': city_name,
                                'timestamp': timestamp,
                                'temperature': temperature,
                                'humidity': humidity,
                                'wind_speed': wind_speed,
                                'sunshine_hours': sunshine_hours,
                                'weather_condition': weather_condition
                            })
                        
                        # 如果API返回的数据不足，使用模拟数据补充
                        if len(data) < hours:
                            for timestamp in time_index[len(data):]:
                                simulated_data = self._generate_simulated_data(timestamp, city_name)
                                data.append(simulated_data.iloc[0].to_dict())
                        
                        continue
                except Exception as e:
                    # 发生异常，使用模拟数据
                    print(f"获取{city_name}天气预报数据失败: {e}")
            
            # 使用模拟数据
            for timestamp in time_index:
                simulated_data = self._generate_simulated_data(timestamp, city_name)
                data.append(simulated_data.iloc[0].to_dict())
        
        return pd.DataFrame(data)
    
    def _get_weather_condition(self, temperature, humidity, wind_speed, sunshine_hours):
        """
        根据天气参数获取天气状况
        
        参数:
        temperature: 温度
        humidity: 湿度
        wind_speed: 风速
        sunshine_hours: 日照时长
        
        返回:
        天气状况字符串
        """
        if sunshine_hours > 6:
            return "晴天"
        elif sunshine_hours > 3:
            return "多云"
        elif humidity > 80:
            return "雨天"
        elif wind_speed > 8:
            return "大风"
        else:
            return "阴天"
    
    def get_weather_impact(self, weather_data):
        """
        计算天气对新能源出力的影响
        
        参数:
        weather_data: 天气数据
        
        返回:
        包含影响因子的DataFrame
        """
        # 计算影响因子
        weather_impact = weather_data.copy()
        
        # 光伏影响因子（与日照时长正相关）
        weather_impact['solar_impact'] = np.clip(weather_impact['sunshine_hours'] * 13 / 12, 0, 1)
        
        # 风电影响因子（与风速正相关，过高或过低都不好）
        weather_impact['wind_impact'] = np.clip((weather_impact['wind_speed'] - 2) / 8, 0, 1)
        
        # 水电影响因子（与湿度正相关）
        weather_impact['hydro_impact'] = np.clip(weather_impact['humidity'] / 100, 0, 1)
        
        return weather_impact

# 创建全局实例
generator = WeatherDataGenerator()

# 模块级函数
def generate_historical_data(hours=1, city=None):
    """生成历史天气数据"""
    return generator.generate_historical_data(hours, city)

@lru_cache(maxsize=32)
def generate_real_time_data(city=None):
    """生成实时天气数据"""
    return generator.generate_real_time_data(city)

@lru_cache(maxsize=1)
def generate_forecast_data(hours=24, city=None):
    """生成预测天气数据"""
    return generator.generate_forecast_data(hours, city)

def get_weather_impact(weather_data):
    """计算天气对新能源出力的影响"""
    return generator.get_weather_impact(weather_data)

# 测试代码
if __name__ == "__main__":
    # 生成历史数据
    historical_data = generate_historical_data(days=1)
    print("历史天气数据:")
    print(historical_data.head())
    
    # 生成实时数据
    real_time_data = generate_real_time_data()
    print("\n实时天气数据:")
    print(real_time_data)
    
    # 生成预测数据
    forecast_data = generate_forecast_data(hours=6)
    print("\n预测天气数据:")
    print(forecast_data)
    
    # 计算天气影响
    weather_impact = get_weather_impact(forecast_data)
    print("\n天气影响因子:")
    print(weather_impact[['timestamp', 'solar_impact', 'wind_impact', 'hydro_impact']])