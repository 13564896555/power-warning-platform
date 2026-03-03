import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
from functools import lru_cache

# 导入配置
from config import AMAP_API_KEY

# 导入模块
import supply_data
import demand_data
import weather_data
import prediction
import ui_components

# 设置页面配置
st.set_page_config(
    page_title="安徽省电力系统预警平台",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 页面标题
st.title("安徽省电力系统预警平台")

# 侧边栏
st.sidebar.title("系统控制")
update_interval = st.sidebar.slider("更新间隔(秒)", 60, 3600, 60)  # 设置默认值为60秒，最小60秒
show_map = st.sidebar.checkbox("显示风险地图", True)

# 初始化会话状态
if 'supply_df' not in st.session_state:
    # 初始加载时使用近一小时的模拟供应数据
    st.session_state.supply_df = supply_data.generate_historical_data(hours=1)

if 'demand_df' not in st.session_state:
    # 初始加载时使用近一小时的模拟需求数据
    st.session_state.demand_df = demand_data.generate_historical_data(hours=1)

if 'weather_df' not in st.session_state:
    # 初始加载时使用近一小时的历史天气数据
    st.session_state.weather_df = weather_data.generate_historical_data(hours=1)

if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()

# 初始化页面状态
if 'page' not in st.session_state:
    st.session_state.page = "overview"

if 'last_page' not in st.session_state:
    st.session_state.last_page = st.session_state.page

# 缓存天气数据，避免频繁调用API
@st.cache_data(ttl=3600)  # 缓存1小时
def get_weather_data():
    """获取天气数据（带缓存）"""
    return weather_data.generate_real_time_data()

@st.cache_data(ttl=3600)  # 缓存1小时
def get_weather_forecast_data(hours=24):
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

# 实时更新数据
def update_data():
    """更新实时数据"""
    # 生成实时供应数据（所有城市）
    real_time_supply = supply_data.generate_real_time_data()
    
    # 生成实时需求数据（所有城市）
    real_time_demand = demand_data.generate_real_time_data()
    
    # 生成实时天气数据（所有城市）
    real_time_weather = get_weather_data()
    
    # 添加到数据框
    st.session_state.supply_df = pd.concat([st.session_state.supply_df, real_time_supply], ignore_index=True)
    st.session_state.demand_df = pd.concat([st.session_state.demand_df, real_time_demand], ignore_index=True)
    st.session_state.weather_df = pd.concat([st.session_state.weather_df, real_time_weather], ignore_index=True)
    
    # 按城市保留最近1小时的数据（每3分钟一个数据点，保留20条）
    cities = st.session_state.supply_df['city'].unique()
    
    # 处理供应数据
    supply_dfs = []
    for city in cities:
        city_supply = st.session_state.supply_df[st.session_state.supply_df['city'] == city]
        # 按时间戳排序
        city_supply = city_supply.sort_values('timestamp')
        if len(city_supply) > 20:
            supply_dfs.append(city_supply.tail(20))
        else:
            supply_dfs.append(city_supply)
    st.session_state.supply_df = pd.concat(supply_dfs, ignore_index=True)
    
    # 处理需求数据
    demand_dfs = []
    for city in cities:
        city_demand = st.session_state.demand_df[st.session_state.demand_df['city'] == city]
        # 按时间戳排序
        city_demand = city_demand.sort_values('timestamp')
        if len(city_demand) > 20:
            demand_dfs.append(city_demand.tail(20))
        else:
            demand_dfs.append(city_demand)
    st.session_state.demand_df = pd.concat(demand_dfs, ignore_index=True)
    
    # 处理天气数据
    weather_dfs = []
    for city in cities:
        city_weather = st.session_state.weather_df[st.session_state.weather_df['city'] == city]
        # 按时间戳排序
        city_weather = city_weather.sort_values('timestamp')
        if len(city_weather) > 20:
            weather_dfs.append(city_weather.tail(20))
        else:
            weather_dfs.append(city_weather)
    st.session_state.weather_df = pd.concat(weather_dfs, ignore_index=True)
    
    # 更新时间
    st.session_state.last_update = datetime.now()

# 检查是否需要更新（仅在当前页面停留时更新，页面切换时不更新）
if 'last_page' not in st.session_state:
    st.session_state.last_page = st.session_state.page

# 只有当页面没有切换且达到更新间隔时才更新数据
current_time = datetime.now()
if st.session_state.page == st.session_state.last_page and (current_time - st.session_state.last_update).total_seconds() >= update_interval:
    update_data()

# 更新最后页面状态
st.session_state.last_page = st.session_state.page

# 计算风险评估
risk_assessment = prediction.assess_system_risk(
    st.session_state.supply_df,
    st.session_state.demand_df,
    st.session_state.weather_df
)

# 计算历史风险数据
historical_risk_df = prediction.generate_historical_risk_data(
    st.session_state.supply_df,
    st.session_state.demand_df,
    st.session_state.weather_df
)

# 计算供需平衡
balance_df = prediction.calculate_supply_demand_balance(
    st.session_state.supply_df,
    st.session_state.demand_df
)

# 主界面导航
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("首页总概"):
        st.session_state.page = "overview"

with col2:
    if st.button("原始数据图表"):
        st.session_state.page = "raw_data"

with col3:
    if st.button("预测数据图表"):
        st.session_state.page = "forecast_data"

with col4:
    if st.button("风险地图"):
        st.session_state.page = "risk_map"

# 初始化页面状态
if 'page' not in st.session_state:
    st.session_state.page = "overview"

# 页面内容
if st.session_state.page == "overview":
    st.subheader("系统概览")
    
    # 风险摘要
    ui_components.display_risk_summary(risk_assessment)
    
    # 供需平衡概览
    st.subheader("电力供需平衡概览")
    
    # 按城市显示供需平衡
    cities = st.session_state.supply_df['city'].unique()
    for city in cities:
        city_balance = balance_df[balance_df['city'] == city]
        if not city_balance.empty:
            st.markdown(f"### {city}")
            balance_fig = ui_components.plot_supply_demand_balance(city_balance)
            st.plotly_chart(balance_fig, use_container_width=True)

elif st.session_state.page == "raw_data":
    st.subheader("原始天气与电力供需数据")
    
    # 选择城市
    cities = st.session_state.supply_df['city'].unique()
    selected_city = st.selectbox("选择城市", cities)
    
    # 过滤数据
    city_supply = st.session_state.supply_df[st.session_state.supply_df['city'] == selected_city]
    city_demand = st.session_state.demand_df[st.session_state.demand_df['city'] == selected_city]
    city_weather = st.session_state.weather_df[st.session_state.weather_df['city'] == selected_city]
    
    # 天气数据图表
    st.subheader(f"{selected_city}天气状况趋势")
    weather_fig = ui_components.plot_weather_impact(city_weather)
    st.plotly_chart(weather_fig, use_container_width=True)
    
    # 电力供应数据
    st.subheader(f"{selected_city}电力供应结构")
    supply_fig = ui_components.plot_supply_breakdown(city_supply)
    st.plotly_chart(supply_fig, use_container_width=True)
    
    # 电力需求数据
    st.subheader(f"{selected_city}电力需求趋势")
    demand_fig = ui_components.plot_demand_trend(city_demand)
    st.plotly_chart(demand_fig, use_container_width=True)
    
    # 详细数据表格
    with st.expander("查看详细数据"):
        tab1, tab2, tab3 = st.tabs(["供应数据", "需求数据", "天气数据"])
        
        with tab1:
            # 只保留整数
            city_supply_int = city_supply.copy()
            numeric_cols = city_supply_int.select_dtypes(include=['number']).columns
            city_supply_int[numeric_cols] = city_supply_int[numeric_cols].round().astype(int)
            st.dataframe(city_supply_int.tail(24))
        
        with tab2:
            # 只保留整数
            city_demand_int = city_demand.copy()
            numeric_cols = city_demand_int.select_dtypes(include=['number']).columns
            city_demand_int[numeric_cols] = city_demand_int[numeric_cols].round().astype(int)
            st.dataframe(city_demand_int.tail(24))
        
        with tab3:
            # 只保留整数
            city_weather_int = city_weather.copy()
            numeric_cols = city_weather_int.select_dtypes(include=['number']).columns
            city_weather_int[numeric_cols] = city_weather_int[numeric_cols].round().astype(int)
            st.dataframe(city_weather_int.tail(24))

elif st.session_state.page == "forecast_data":
    st.subheader("预测电力系统供需数据")
    
    # 选择城市
    cities = st.session_state.supply_df['city'].unique()
    selected_city = st.selectbox("选择城市", cities)
    
    # 过滤预测数据
    city_forecast = risk_assessment['forecast_data'][risk_assessment['forecast_data']['city'] == selected_city]
    
    # 24小时预测
    st.subheader(f"{selected_city}24小时电力供需预测")
    forecast_fig = ui_components.plot_prediction_forecast(city_forecast)
    st.plotly_chart(forecast_fig, use_container_width=True)
    
    # 预测数据表格
    st.subheader(f"{selected_city}预测详细数据")
    # 只保留整数
    city_forecast_int = city_forecast.copy()
    numeric_cols = city_forecast_int.select_dtypes(include=['number']).columns
    city_forecast_int[numeric_cols] = city_forecast_int[numeric_cols].round().astype(int)
    st.dataframe(city_forecast_int)

elif st.session_state.page == "risk_map":
    st.subheader("预测电力系统供需风险图")
    
    # 风险地图 - 使用与首页概览相同的风险等级
    map_html = ui_components.create_amap_risk_map(risk_assessment['city_risks'], AMAP_API_KEY)
    st.components.v1.html(map_html, height=600)
    
    # 风险等级说明
    st.subheader("风险等级说明")
    st.markdown("- **低风险**：供需平衡，系统稳定")
    st.markdown("- **中等风险**：供需基本平衡，需要关注")
    st.markdown("- **高风险**：供需失衡，需要采取措施")
    st.markdown("- **严重风险**：供需严重失衡，紧急应对")



# 系统信息
st.sidebar.info(f"上次更新: {st.session_state.last_update.strftime('%Y-%m-%d %H:%M:%S')}")
st.sidebar.info(f"数据点数: {len(st.session_state.supply_df)}")

# 自动刷新按钮
if st.sidebar.button("立即更新"):
    update_data()
    st.rerun()

# 运行状态
st.sidebar.success("系统运行正常")