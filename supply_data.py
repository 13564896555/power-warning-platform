import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class SupplyDataGenerator:
    """
    电力供应数据生成器
    包括火电、光伏、风电、水电四种发电方式
    """
    
    def __init__(self):
        # 安徽省市级行政区
        self.cities = [
            "合肥市", "芜湖市", "蚌埠市", "淮南市", "马鞍山市",
            "淮北市", "铜陵市", "安庆市", "黄山市", "滁州市",
            "阜阳市", "宿州市", "六安市", "亳州市", "池州市", "宣城市"
        ]
        
        # 基础参数设置
        self.base_coal_power = 10000  # 基础火电出力 (MW)
        self.base_solar_power = 2000   # 基础光伏出力 (MW)
        self.base_wind_power = 1500    # 基础风电出力 (MW)
        self.base_hydro_power = 1000   # 基础水电出力 (MW)
        
        # 波动参数
        self.coal_variation = 0.05     # 火电波动系数
        self.solar_variation = 0.3      # 光伏波动系数
        self.wind_variation = 0.4       # 风电波动系数
        self.hydro_variation = 0.2      # 水电波动系数
        
        # 时间相关参数
        self.time_pattern = np.sin(np.linspace(0, 2*np.pi, 24))  # 24小时出力模式
    
    def generate_historical_data(self, hours=1, city=None):
        """
        生成历史供应数据
        
        参数:
        hours: 生成数据的小时数
        city: 城市名称，None示所有城市
        
        返回:
        包含历史供应数据的DataFrame
        """
        # 生成时间序列
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        time_index = pd.date_range(start=start_time, end=end_time, freq='3T')
        
        # 生成各种电源的出力数据
        data = []
        
        # 确定要处理的城市
        cities_to_process = [city] if city and city in self.cities else self.cities
        
        for city_name in cities_to_process:
            # 为每个城市添加一些随机差异
            city_factor = hash(city_name) % 10 / 10  # 0-1之间的城市因子
            
            for timestamp in time_index:
                hour = timestamp.hour
                
                # 火电出力（相对稳定，略有波动）
                coal_power = self.base_coal_power * (1 + city_factor * 0.1) * (1 + self.coal_variation * np.random.normal())
                
                # 光伏出力（白天有，晚上无）
                solar_factor = max(0, np.sin((hour - 6) * np.pi / 10))  # 6-16点有出力
                solar_power = self.base_solar_power * (1 + city_factor * 0.15) * solar_factor * (1 + self.solar_variation * np.random.normal())
                
                # 风电出力（有随机性）
                wind_power = self.base_wind_power * (1 + city_factor * 0.2) * (1 + self.wind_variation * np.random.normal())
                
                # 水电出力（相对稳定）
                hydro_power = self.base_hydro_power * (1 + city_factor * 0.1) * (1 + self.hydro_variation * np.random.normal())
                
                # 计算总出力
                total_power = coal_power + solar_power + wind_power + hydro_power
                
                data.append({
                    'city': city_name,
                    'timestamp': timestamp,
                    'thermal': max(0, coal_power),
                    'solar': max(0, solar_power),
                    'wind': max(0, wind_power),
                    'hydro': max(0, hydro_power),
                    'total_supply': max(0, total_power)
                })
        
        return pd.DataFrame(data)
    
    def generate_real_time_data(self, city=None):
        """
        生成实时供应数据
        
        参数:
        city: 城市名称，None表示所有城市
        
        返回:
        包含实时供应数据的DataFrame
        """
        timestamp = datetime.now()
        hour = timestamp.hour
        data = []
        
        # 确定要处理的城市
        cities_to_process = [city] if city and city in self.cities else self.cities
        
        for city_name in cities_to_process:
            # 为每个城市添加一些随机差异
            city_factor = hash(city_name) % 10 / 10  # 0-1之间的城市因子
            
            # 火电出力
            coal_power = self.base_coal_power * (1 + city_factor * 0.1) * (1 + self.coal_variation * np.random.normal())
            
            # 光伏出力
            solar_factor = max(0, np.sin((hour - 6) * np.pi / 10))
            solar_power = self.base_solar_power * (1 + city_factor * 0.15) * solar_factor * (1 + self.solar_variation * np.random.normal())
            
            # 风电出力
            wind_power = self.base_wind_power * (1 + city_factor * 0.2) * (1 + self.wind_variation * np.random.normal())
            
            # 水电出力
            hydro_power = self.base_hydro_power * (1 + city_factor * 0.1) * (1 + self.hydro_variation * np.random.normal())
            
            # 计算总出力
            total_power = coal_power + solar_power + wind_power + hydro_power
            
            data.append({
                'city': city_name,
                'timestamp': timestamp,
                'thermal': max(0, coal_power),
                'solar': max(0, solar_power),
                'wind': max(0, wind_power),
                'hydro': max(0, hydro_power),
                'total_supply': max(0, total_power)
            })
        
        return pd.DataFrame(data)
    
    def generate_forecast_data(self, hours=24, city=None):
        """
        生成未来供应预测数据
        
        参数:
        hours: 预测小时数
        city: 城市名称，None表示所有城市
        
        返回:
        包含预测供应数据的DataFrame
        """
        # 生成时间序列
        start_time = datetime.now()
        time_index = pd.date_range(start=start_time, periods=hours*20, freq='3T')
        
        # 生成预测数据
        data = []
        
        # 确定要处理的城市
        cities_to_process = [city] if city and city in self.cities else self.cities
        
        for city_name in cities_to_process:
            # 为每个城市添加一些随机差异
            city_factor = hash(city_name) % 10 / 10  # 0-1之间的城市因子
            
            for timestamp in time_index:
                hour = timestamp.hour
                
                # 火电出力预测
                coal_power = self.base_coal_power * (1 + city_factor * 0.1) * (1 + self.coal_variation * np.random.normal())
                
                # 光伏出力预测
                solar_factor = max(0, np.sin((hour - 6) * np.pi / 10))
                solar_power = self.base_solar_power * (1 + city_factor * 0.15) * solar_factor * (1 + self.solar_variation * np.random.normal())
                
                # 风电出力预测
                wind_power = self.base_wind_power * (1 + city_factor * 0.2) * (1 + self.wind_variation * np.random.normal())
                
                # 水电出力预测
                hydro_power = self.base_hydro_power * (1 + city_factor * 0.1) * (1 + self.hydro_variation * np.random.normal())
                
                # 计算总出力
                total_power = coal_power + solar_power + wind_power + hydro_power
                
                data.append({
                    'city': city_name,
                    'timestamp': timestamp,
                    'thermal': max(0, coal_power),
                    'solar': max(0, solar_power),
                    'wind': max(0, wind_power),
                    'hydro': max(0, hydro_power),
                    'total_supply': max(0, total_power)
                })
        
        return pd.DataFrame(data)

# 创建全局实例
generator = SupplyDataGenerator()

# 模块级函数
def generate_historical_data(hours=1, city=None):
    """生成历史供应数据"""
    return generator.generate_historical_data(hours, city)

def generate_real_time_data(city=None):
    """生成实时供应数据"""
    return generator.generate_real_time_data(city)

def generate_forecast_data(hours=24, city=None):
    """生成预测供应数据"""
    return generator.generate_forecast_data(hours, city)

# 测试代码
if __name__ == "__main__":
    # 生成历史数据
    historical_data = generate_historical_data(days=1)
    print("历史供应数据:")
    print(historical_data.head())
    
    # 生成实时数据
    real_time_data = generate_real_time_data()
    print("\n实时供应数据:")
    print(real_time_data)
    
    # 生成预测数据
    forecast_data = generate_forecast_data(hours=6)
    print("\n预测供应数据:")
    print(forecast_data)
