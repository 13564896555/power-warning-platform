import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class DemandDataGenerator:
    """
    用户端用电数据生成器
    模拟安徽省用户端的用电情况
    """
    
    def __init__(self):
        # 安徽省市级行政区
        self.cities = [
            "合肥市", "芜湖市", "蚌埠市", "淮南市", "马鞍山市",
            "淮北市", "铜陵市", "安庆市", "黄山市", "滁州市",
            "阜阳市", "宿州市", "六安市", "亳州市", "池州市", "宣城市"
        ]
        
        # 基础参数设置
        self.base_demand = 12000  # 基础用电需求 (MW)
        
        # 波动参数
        self.demand_variation = 0.15  # 用电需求波动系数
        
        # 时间相关参数
        self.hourly_pattern = np.array([0.7, 0.6, 0.5, 0.4, 0.4, 0.5, 0.8, 1.0, 1.1, 1.0, 0.9, 0.9, 
                                       1.0, 1.0, 0.9, 1.0, 1.2, 1.3, 1.2, 1.1, 1.0, 0.9, 0.8, 0.7])  # 24小时用电模式
        
        self.weekly_pattern = np.array([0.9, 0.9, 0.9, 0.9, 1.0, 1.2, 1.1])  # 7天用电模式
    
    def generate_historical_data(self, hours=1, city=None):
        """
        生成历史用电数据
        
        参数:
        hours: 生成数据的小时数
        city: 城市名称,None表示所有城市
        
        返回:
        包含历史用电数据的DataFrame
        """
        # 生成时间序列
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        time_index = pd.date_range(start=start_time, end=end_time, freq='3T')
        
        # 生成用电需求数据
        data = []
        
        # 确定要处理的城市
        cities_to_process = [city] if city and city in self.cities else self.cities
        
        for city_name in cities_to_process:
            # 为每个城市添加一些随机差异
            city_factor = hash(city_name) % 10 / 10  # 0-1之间的城市因子
            
            for timestamp in time_index:
                hour = timestamp.hour
                weekday = timestamp.weekday()
                
                # 计算时间因子
                hour_factor = self.hourly_pattern[hour]
                weekday_factor = self.weekly_pattern[weekday]
                
                # 计算用电需求
                demand = self.base_demand * (1 + city_factor * 0.2) * hour_factor * weekday_factor * (1 + self.demand_variation * np.random.normal())
                
                data.append({
                    'city': city_name,
                    'timestamp': timestamp,
                    'demand': max(0, demand)
                })
        
        return pd.DataFrame(data)
    
    def generate_real_time_data(self, city=None):
        """
        生成实时用电数据
        
        参数:
        city: 城市名称,None表示所有城市
        
        返回:
        包含实时用电数据的DataFrame
        """
        timestamp = datetime.now()
        hour = timestamp.hour
        weekday = timestamp.weekday()
        data = []
        
        # 确定要处理的城市
        cities_to_process = [city] if city and city in self.cities else self.cities
        
        for city_name in cities_to_process:
            # 为每个城市添加一些随机差异
            city_factor = hash(city_name) % 10 / 10  # 0-1之间的城市因子
            
            # 计算时间因子
            hour_factor = self.hourly_pattern[hour]
            weekday_factor = self.weekly_pattern[weekday]
            
            # 计算用电需求
            demand = self.base_demand * (1 + city_factor * 0.2) * hour_factor * weekday_factor * (1 + self.demand_variation * np.random.normal())
            
            data.append({
                'city': city_name,
                'timestamp': timestamp,
                'demand': max(0, demand)
            })
        
        return pd.DataFrame(data)
    
    def generate_forecast_data(self, hours=24, city=None):
        """
        生成未来用电预测数据
        
        参数:
        hours: 预测小时数
        city: 城市名称,None表示所有城市
        
        返回:
        包含预测用电数据的DataFrame
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
                weekday = timestamp.weekday()
                
                # 计算时间因子
                hour_factor = self.hourly_pattern[hour]
                weekday_factor = self.weekly_pattern[weekday]
                
                # 计算用电需求预测
                demand = self.base_demand * (1 + city_factor * 0.2) * hour_factor * weekday_factor * (1 + self.demand_variation * np.random.normal())
                
                data.append({
                    'city': city_name,
                    'timestamp': timestamp,
                    'demand': max(0, demand)
                })
        
        return pd.DataFrame(data)

# 创建全局实例
generator = DemandDataGenerator()

# 模块级函数
def generate_historical_data(hours=1, city=None):
    """生成历史用电数据"""
    return generator.generate_historical_data(hours, city)

def generate_real_time_data(city=None):
    """生成实时用电数据"""
    return generator.generate_real_time_data(city)

def generate_forecast_data(hours=24, city=None):
    """生成预测用电数据"""
    return generator.generate_forecast_data(hours, city)

# 测试代码
if __name__ == "__main__":
    # 生成历史数据
    historical_data = generate_historical_data(days=1)
    print("历史用电数据:")
    print(historical_data.head())
    
    # 生成实时数据
    real_time_data = generate_real_time_data()
    print("\n实时用电数据:")
    print(real_time_data)
    
    # 生成预测数据
    forecast_data = generate_forecast_data(hours=6)
    print("\n预测用电数据:")
    print(forecast_data)
