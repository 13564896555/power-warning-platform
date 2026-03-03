import pandas as pd
import numpy as np
from datetime import timedelta
from functools import lru_cache
import supply_data
import demand_data
import weather_data

def calculate_supply_demand_balance(supply_df, demand_df):
    """计算供需平衡"""
    # 合并供需数据（按城市和时间戳）
    merged_df = pd.merge(supply_df, demand_df, on=['city', 'timestamp'], how='outer')
    merged_df = merged_df.sort_values(['city', 'timestamp'])
    merged_df = merged_df.fillna(method='ffill')
    
    # 计算总供应
    merged_df['total_supply'] = merged_df['thermal'] + merged_df['solar'] + merged_df['wind'] + merged_df['hydro']
    
    # 计算供需平衡
    merged_df['balance'] = merged_df['total_supply'] - merged_df['demand']
    
    return merged_df

def calculate_risk_level(balance):
    """计算风险等级"""
    if balance >= 1000:
        return 0, "安全"
    elif balance >= 500:
        return 1, "低风险"
    elif balance >= 0:
        return 2, "中风险"
    elif balance >= -500:
        return 3, "高风险"
    else:
        return 4, "严重风险"

# 缓存天气预测数据，避免频繁调用API
@lru_cache(maxsize=1)
def get_cached_weather_forecast(hours=24):
    """获取所有城市的天气预测数据（带缓存）"""
    # 获取所有城市
    cities = ["合肥市", "芜湖市", "蚌埠市", "淮南市", "马鞍山市",
             "淮北市", "铜陵市", "安庆市", "黄山市", "滁州市",
             "阜阳市", "宿州市", "六安市", "亳州市", "池州市", "宣城市"]
    
    # 为每个城市获取天气预测数据
    forecast_data = []
    for city in cities:
        city_forecast = weather_data.generate_forecast_data(hours, city)
        forecast_data.append(city_forecast)
    
    # 合并所有城市的预测数据
    return pd.concat(forecast_data, ignore_index=True)

def generate_prediction_data(supply_df, demand_df, weather_df, hours=24):
    """生成预测数据"""
    # 获取所有城市
    cities = supply_df['city'].unique()
    
    # 获取最新时间
    latest_time = supply_df['timestamp'].max()
    
    # 生成未来时间点
    future_times = [latest_time + timedelta(hours=i) for i in range(1, hours+1)]
    
    # 生成预测数据
    prediction_data = []
    
    # 获取所有城市的天气预测数据（使用缓存）
    all_weather_forecast = get_cached_weather_forecast(hours)
    
    for city in cities:
        # 过滤当前城市的天气预测数据
        weather_forecast = all_weather_forecast[all_weather_forecast['city'] == city]
        
        for i, timestamp in enumerate(future_times):
            # 生成供应预测
            supply_pred = supply_data.generate_forecast_data(hours=1, city=city)
            
            # 生成需求预测
            demand_pred = demand_data.generate_forecast_data(hours=1, city=city)
            
            # 从缓存的天气预测中获取对应时间的数据
            if i < len(weather_forecast):
                # 尝试根据时间戳获取数据
                filtered_weather = weather_forecast[weather_forecast['timestamp'] == timestamp]
                if not filtered_weather.empty:
                    weather_pred = filtered_weather.iloc[0]
                else:
                    # 如果没有找到匹配的时间戳，使用模拟数据
                    weather_pred = weather_data.generate_real_time_data(city=city).iloc[0]
            else:
                # 如果预测数据不足，生成模拟数据
                weather_pred = weather_data.generate_real_time_data(city=city).iloc[0]
            
            # 计算天气影响
            weather_impact = weather_data.get_weather_impact(pd.DataFrame([weather_pred]))
            
            # 调整供应预测
            adjusted_solar = supply_pred['solar'].iloc[0] * weather_impact['solar_impact'].iloc[0]
            adjusted_wind = supply_pred['wind'].iloc[0] * weather_impact['wind_impact'].iloc[0]
            adjusted_hydro = supply_pred['hydro'].iloc[0] * weather_impact['hydro_impact'].iloc[0]
            
            total_supply = supply_pred['thermal'].iloc[0] + adjusted_solar + adjusted_wind + adjusted_hydro
            
            # 计算供需平衡
            balance = total_supply - demand_pred['demand'].iloc[0]
            
            # 计算风险等级
            risk_level, risk_description = calculate_risk_level(balance)
            
            prediction_data.append({
                'city': city,
                'timestamp': timestamp,
                'thermal': supply_pred['thermal'].iloc[0],
                'solar': adjusted_solar,
                'wind': adjusted_wind,
                'hydro': adjusted_hydro,
                'total_supply': total_supply,
                'demand': demand_pred['demand'].iloc[0],
                'balance': balance,
                'risk_level': risk_level,
                'risk_description': risk_description,
                'temperature': weather_pred['temperature'],
                'humidity': weather_pred['humidity'],
                'wind_speed': weather_pred['wind_speed'],
                'sunshine_hours': weather_pred['sunshine_hours']
            })
    
    return pd.DataFrame(prediction_data)

def assess_system_risk(supply_df, demand_df, weather_df):
    """评估系统风险"""
    # 获取所有城市
    cities = supply_df['city'].unique()
    
    # 生成未来24小时预测
    forecast_df = generate_prediction_data(supply_df, demand_df, weather_df)
    
    # 计算每个城市的风险
    city_risks = {}
    for city in cities:
        # 过滤当前城市的数据
        city_supply = supply_df[supply_df['city'] == city]
        city_demand = demand_df[demand_df['city'] == city]
        
        # 计算当前供需平衡
        current_balance_df = calculate_supply_demand_balance(city_supply, city_demand)
        # 获取最新的平衡值
        if not current_balance_df.empty:
            current_balance = current_balance_df.sort_values('timestamp').tail(1)['balance'].iloc[0]
        else:
            # 如果没有数据，使用默认值
            current_balance = 1000  # 默认为安全
        
        # 确保balance不是nan
        if pd.isna(current_balance):
            current_balance = 1000  # 默认为安全
        
        current_risk, current_risk_desc = calculate_risk_level(current_balance)
        
        # 过滤当前城市的预测数据
        city_forecast = forecast_df[forecast_df['city'] == city]
        
        # 计算预测期间的最大风险
        max_risk_level = city_forecast['risk_level'].max()
        max_risk_time = city_forecast[city_forecast['risk_level'] == max_risk_level]['timestamp'].iloc[0]
        max_risk_desc = city_forecast[city_forecast['risk_level'] == max_risk_level]['risk_description'].iloc[0]
        
        # 计算风险趋势
        risk_trend = city_forecast['risk_level'].values[-1] - city_forecast['risk_level'].values[0]
        if risk_trend > 0:
            trend_desc = "风险上升"
        elif risk_trend < 0:
            trend_desc = "风险下降"
        else:
            trend_desc = "风险稳定"
        
        city_risks[city] = {
            'current_risk': current_risk,
            'current_risk_description': current_risk_desc,
            'current_balance': current_balance,
            'max_forecast_risk': max_risk_level,
            'max_forecast_risk_time': max_risk_time,
            'max_forecast_risk_description': max_risk_desc,
            'risk_trend': risk_trend,
            'risk_trend_description': trend_desc
        }
    
    # 计算整个系统的总体风险
    overall_current_risk = max([risk['current_risk'] for risk in city_risks.values()])
    overall_max_risk = max([risk['max_forecast_risk'] for risk in city_risks.values()])
    
    # 获取总体风险描述
    _, overall_current_risk_desc = calculate_risk_level(0)  # 临时值，后续会更新
    _, overall_max_risk_desc = calculate_risk_level(0)  # 临时值，后续会更新
    
    for risk in city_risks.values():
        if risk['current_risk'] == overall_current_risk:
            overall_current_risk_desc = risk['current_risk_description']
        if risk['max_forecast_risk'] == overall_max_risk:
            overall_max_risk_desc = risk['max_forecast_risk_description']
    
    return {
        'city_risks': city_risks,
        'current_risk': overall_current_risk,
        'current_risk_description': overall_current_risk_desc,
        'max_forecast_risk': overall_max_risk,
        'max_forecast_risk_description': overall_max_risk_desc,
        'forecast_data': forecast_df
    }

def generate_historical_risk_data(supply_df, demand_df):
    """生成历史风险数据"""
    # 计算历史供需平衡
    balance_df = calculate_supply_demand_balance(supply_df, demand_df)
    
    # 计算历史风险
    balance_df['risk_level'] = balance_df['balance'].apply(lambda x: calculate_risk_level(x)[0])
    balance_df['risk_description'] = balance_df['balance'].apply(lambda x: calculate_risk_level(x)[1])
    
    return balance_df