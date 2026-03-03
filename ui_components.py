import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json

def plot_supply_demand_balance(balance_df):
    """绘制供需平衡图"""
    fig = go.Figure()
    
    # 添加供应数据
    fig.add_trace(go.Bar(
        x=balance_df['timestamp'],
        y=balance_df['total_supply'],
        name='总供应',
        marker_color='#4CAF50'
    ))
    
    # 添加需求数据
    fig.add_trace(go.Bar(
        x=balance_df['timestamp'],
        y=balance_df['demand'],
        name='需求',
        marker_color='#FF5722'
    ))
    
    # 添加平衡线
    fig.add_trace(go.Scatter(
        x=balance_df['timestamp'],
        y=balance_df['balance'],
        name='供需平衡',
        mode='lines+markers',
        line=dict(color='#2196F3', width=2)
    ))
    
    # 更新布局
    fig.update_layout(
        title='电力供需平衡',
        xaxis_title='时间',
        yaxis_title='电力(MW)',
        barmode='group',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=400,
        xaxis=dict(
            dtick=180000,  # 3分钟的毫秒数
            tickformat='%H:%M',
            tickangle=45,
            tickmode='linear',
            range=[balance_df['timestamp'].iloc[-1] - pd.Timedelta(hours=1), balance_df['timestamp'].iloc[-1]]
        ),
        # 添加缩放功能
        hovermode='x unified',
        dragmode='pan',
        margin=dict(l=50, r=50, t=50, b=100)
    )
    
    # 添加缩放控件
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=15, label="15m", step="minute", stepmode="backward"),
                dict(count=30, label="30m", step="minute", stepmode="backward"),
                dict(count=1, label="1h", step="hour", stepmode="backward"),
                dict(step="all")
            ])
        )
    )
    
    return fig

def plot_supply_breakdown(supply_df):
    """绘制供应结构分解图"""
    # 选择数值列并计算平均值
    numeric_cols = ['thermal', 'solar', 'wind', 'hydro']
    supply_avg = supply_df[numeric_cols].mean()
    
    # 创建数据
    data = {
        '能源类型': ['火电', '光伏', '风电', '水电'],
        '供应量(MW)': [supply_avg['thermal'], supply_avg['solar'], supply_avg['wind'], supply_avg['hydro']]
    }
    
    df = pd.DataFrame(data)
    
    # 创建饼图
    fig = px.pie(
        df,
        values='供应量(MW)',
        names='能源类型',
        title='电力供应结构',
        color_discrete_sequence=['#FF9800', '#FFEB3B', '#2196F3', '#00BCD4']
    )
    
    return fig

def plot_demand_trend(demand_df):
    """绘制需求趋势图"""
    fig = px.bar(
        demand_df,
        x='timestamp',
        y='demand',
        title='电力需求趋势',
        labels={'timestamp': '时间', 'demand': '需求(MW)'},
        color_discrete_sequence=['#FF5722']
    )
    
    fig.update_layout(
        height=400,
        xaxis=dict(
            dtick=180000,  # 3分钟的毫秒数
            tickformat='%H:%M',
            tickangle=45,
            tickmode='linear',
            range=[demand_df['timestamp'].iloc[-1] - pd.Timedelta(hours=1), demand_df['timestamp'].iloc[-1]]
        ),
        # 添加缩放功能
        hovermode='x unified',
        dragmode='pan',
        margin=dict(l=50, r=50, t=50, b=100)
    )
    
    # 添加缩放控件
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=15, label="15m", step="minute", stepmode="backward"),
                dict(count=30, label="30m", step="minute", stepmode="backward"),
                dict(count=1, label="1h", step="hour", stepmode="backward"),
                dict(step="all")
            ])
        )
    )
    
    return fig

def plot_weather_impact(weather_df):
    """绘制天气影响图"""
    fig = px.bar(
        weather_df,
        x='timestamp',
        y=['temperature', 'humidity', 'wind_speed', 'sunshine_hours'],
        title='天气状况',
        labels={'timestamp': '时间', 'value': '数值'},
        color_discrete_sequence=['#FF9800', '#2196F3', '#9C27B0', '#4CAF50']
    )
    
    fig.update_layout(
        height=400,
        xaxis=dict(
            dtick=180000,  # 3分钟的毫秒数
            tickformat='%H:%M',
            tickangle=45,
            tickmode='linear',
            range=[weather_df['timestamp'].iloc[-1] - pd.Timedelta(hours=1), weather_df['timestamp'].iloc[-1]]
        ),
        # 添加缩放功能
        hovermode='x unified',
        dragmode='pan',
        margin=dict(l=50, r=50, t=50, b=100)
    )
    
    # 添加缩放控件
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=15, label="15m", step="minute", stepmode="backward"),
                dict(count=30, label="30m", step="minute", stepmode="backward"),
                dict(count=1, label="1h", step="hour", stepmode="backward"),
                dict(step="all")
            ])
        )
    )
    
    return fig

def plot_risk_heatmap(risk_df):
    """绘制风险热力图"""
    # 准备热力图数据
    # 创建时间和风险等级的矩阵
    risk_matrix = []
    timestamps = []
    
    # 按小时分组
    hourly_groups = risk_df.groupby(risk_df['timestamp'].dt.hour)
    
    for hour, group in hourly_groups:
        timestamps.append(f'{hour}:00')
        # 计算每个风险等级的出现次数
        risk_counts = group['risk_level'].value_counts().sort_index()
        # 填充缺失的风险等级
        for level in range(5):
            if level not in risk_counts:
                risk_counts[level] = 0
        risk_matrix.append(risk_counts.sort_index().values)
    
    # 创建热力图
    fig = go.Figure(data=go.Heatmap(
        z=risk_matrix,
        x=['安全', '低风险', '中风险', '高风险', '严重风险'],
        y=timestamps,
        colorscale='YlOrRd',
        colorbar=dict(title='出现次数')
    ))
    
    fig.update_layout(
        title='风险等级热力图',
        xaxis_title='风险等级',
        yaxis_title='小时',
        height=400
    )
    
    return fig

def plot_prediction_forecast(forecast_df):
    """绘制预测趋势图"""
    fig = go.Figure()
    
    # 添加供应预测
    fig.add_trace(go.Bar(
        x=forecast_df['timestamp'],
        y=forecast_df['total_supply'],
        name='供应预测',
        marker_color='#4CAF50'
    ))
    
    # 添加需求预测
    fig.add_trace(go.Bar(
        x=forecast_df['timestamp'],
        y=forecast_df['demand'],
        name='需求预测',
        marker_color='#FF5722'
    ))
    
    # 添加平衡线
    fig.add_trace(go.Scatter(
        x=forecast_df['timestamp'],
        y=forecast_df['balance'],
        name='供需平衡',
        mode='lines+markers',
        line=dict(color='#2196F3', width=2)
    ))
    
    # 添加风险等级标记
    for i, row in forecast_df.iterrows():
        fig.add_annotation(
            x=row['timestamp'],
            y=row['balance'],
            text=row['risk_description'],
            showarrow=True,
            arrowhead=1,
            font=dict(size=10)
        )
    
    # 更新布局
    fig.update_layout(
        title='24小时电力供需预测',
        xaxis_title='时间',
        yaxis_title='电力(MW)',
        barmode='group',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=400,
        xaxis=dict(
            dtick=3600000,  # 1小时的毫秒数
            tickformat='%H:%M\n%m-%d',
            tickangle=45,
            tickmode='linear'
        ),
        # 添加缩放功能
        hovermode='x unified',
        dragmode='pan',
        margin=dict(l=50, r=50, t=50, b=100)
    )
    
    # 添加缩放控件
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=3, label="3h", step="hour", stepmode="backward"),
                dict(count=6, label="6h", step="hour", stepmode="backward"),
                dict(count=12, label="12h", step="hour", stepmode="backward"),
                dict(count=24, label="24h", step="hour", stepmode="backward"),
                dict(step="all")
            ])
        )
    )
    
    return fig

def display_risk_summary(risk_assessment):
    """显示风险摘要"""
    # 创建风险等级对应的颜色
    risk_colors = {
        0: '#4CAF50',  # 安全
        1: '#8BC34A',  # 低风险
        2: '#FFC107',  # 中风险
        3: '#FF9800',  # 高风险
        4: '#F44336'   # 严重风险
    }
    
    # 获取当前风险颜色
    current_risk_color = risk_colors.get(risk_assessment['current_risk'], '#9E9E9E')
    
    # 创建摘要卡片
    st.subheader('系统风险摘要')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info('当前状态')
        st.markdown(f"""**当前风险等级:** <span style="color:{current_risk_color}; font-size:18px;">{risk_assessment['current_risk_description']}</span>""", unsafe_allow_html=True)
    
    with col2:
        st.warning('预测状态')
        st.write(f"**最大预测风险:** {risk_assessment['max_forecast_risk_description']}")
    
    # 显示各城市风险
    st.subheader('各城市风险状况')
    city_risks = risk_assessment.get('city_risks', {})
    
    # 创建网格布局
    cols = st.columns(4)
    for i, (city, risk) in enumerate(city_risks.items()):
        with cols[i % 4]:
            city_risk_color = risk_colors.get(risk['current_risk'], '#9E9E9E')
            st.markdown(f"**{city}**")
            st.markdown(f"""**风险等级:** <span style="color:{city_risk_color};">{risk['current_risk_description']}</span>""", unsafe_allow_html=True)
            st.write(f"**供需平衡:** {risk['current_balance']:.2f} MW")

def display_weather_summary(weather_df):
    """显示天气摘要"""
    # 获取所有城市
    cities = weather_df['city'].unique()
    
    st.subheader('天气状况')
    
    # 为每个城市显示天气数据
    for city in cities:
        # 获取该城市的最新天气数据
        city_weather = weather_df[weather_df['city'] == city].tail(1).iloc[0]
        
        st.markdown(f"### {city}")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("温度", f"{city_weather['temperature']:.1f}°C")
        
        with col2:
            st.metric("湿度", f"{city_weather['humidity']:.1f}%")
        
        with col3:
            st.metric("风速", f"{city_weather['wind_speed']:.1f} m/s")
        
        with col4:
            st.metric("日照时长", f"{city_weather['sunshine_hours']:.1f} 小时")

def create_amap_risk_map(city_risks, api_key):
    """创建高德地图风险地图"""
    # 安徽省市级行政区坐标（示例数据）
    city_coords = {
        "合肥市": [117.2808, 31.8639],
        "芜湖市": [118.3893, 31.3386],
        "蚌埠市": [117.3868, 32.9274],
        "淮南市": [117.0303, 32.6395],
        "马鞍山市": [118.4811, 31.5384],
        "淮北市": [116.7981, 33.9693],
        "铜陵市": [117.8173, 30.9467],
        "安庆市": [117.0574, 30.5232],
        "黄山市": [118.1752, 29.7028],
        "滁州市": [118.3192, 32.3068],
        "阜阳市": [115.8157, 32.8975],
        "宿州市": [116.9836, 33.6317],
        "六安市": [116.5075, 31.7433],
        "亳州市": [115.7817, 33.8611],
        "池州市": [117.4849, 30.6614],
        "宣城市": [118.7567, 30.9402]
    }
    
    # 生成城市风险数据
    city_risk_data = []
    
    # 使用city_risks中的当前风险等级
    for city, coords in city_coords.items():
        if city in city_risks:
            # 从city_risks中获取当前风险等级
            risk_level = city_risks[city]['current_risk']
            risk_description = city_risks[city]['current_risk_description']
        else:
            # 如果没有数据，默认为安全
            risk_level = 0
            risk_description = '安全'
        
        # 转换为Python原生整数类型
        risk_level = int(risk_level)
        
        city_risk_data.append({
            'name': city,
            'lng': float(coords[0]),
            'lat': float(coords[1]),
            'risk_level': risk_level,
            'risk_description': risk_description
        })
    
    # 生成地图HTML
    map_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="initial-scale=1.0, user-scalable=yes, width=device-width">
        <title>安徽省电力风险地图</title>
        <link rel="stylesheet" href="https://a.amap.com/jsapi_demos/static/demo-center/css/demo-center.css" />
        <script type="text/javascript" src="https://webapi.amap.com/maps?v=2.0&key={api_key}"></script>
        <script type="text/javascript" src="https://a.amap.com/jsapi_demos/static/demo-center/js/demoutils.js"></script>
    </head>
    <body>
        <div id="container"></div>
        <script>
            // 等待DOM加载完成
            window.onload = function() {
                // 初始化地图
                var map = new AMap.Map('container', {
                    zoom: 7,
                    center: [117.2808, 31.8639],
                    layers: [new AMap.TileLayer()],
                    zooms: [3, 20]
                });
                
                // 城市风险数据
                var cityRiskData = {city_risk_data};
                console.log('城市风险数据:', cityRiskData);
                
                // 风险等级对应的颜色
                var riskColors = ['#4CAF50', '#8BC34A', '#FFC107', '#FF9800', '#F44336'];
                
                // 风险等级对应的图标
                var riskIcons = [
                    'https://a.amap.com/jsapi_demos/static/demo-center/icons/poi-marker-green.png',
                    'https://a.amap.com/jsapi_demos/static/demo-center/icons/poi-marker-green.png',
                    'https://a.amap.com/jsapi_demos/static/demo-center/icons/poi-marker-yellow.png',
                    'https://a.amap.com/jsapi_demos/static/demo-center/icons/poi-marker-orange.png',
                    'https://a.amap.com/jsapi_demos/static/demo-center/icons/poi-marker-red.png'
                ];
                
                // 检查数据是否有效
                if (Array.isArray(cityRiskData)) {
                    console.log('数据是数组，长度:', cityRiskData.length);
                    // 添加标记
                    cityRiskData.forEach(function(city) {
                        console.log('添加城市标记:', city.name, city.risk_level);
                        
                        // 确保风险等级是数字
                        var riskLevel = parseInt(city.risk_level) || 0;
                        riskLevel = Math.max(0, Math.min(4, riskLevel));
                        
                        // 创建标记
                        var marker = new AMap.Marker({
                            position: [city.lng, city.lat],
                            title: city.name,
                            icon: new AMap.Icon({
                                size: new AMap.Size(40, 40),
                                image: riskIcons[riskLevel],
                                imageSize: new AMap.Size(40, 40)
                            }),
                            label: {
                                offset: new AMap.Pixel(45, 0),
                                content: '<div style="background-color:' + riskColors[riskLevel] + '; color:white; padding:4px 12px; border-radius:15px; font-size:14px; white-space:nowrap; font-weight:bold;">' + city.risk_description + '</div>',
                                direction: 'right'
                            }
                        });
                        
                        // 添加到地图
                        marker.setMap(map);
                        
                        // 添加信息窗口
                        var infoWindow = new AMap.InfoWindow({
                            content: '<h3 style="margin-top:0;">' + city.name + '</h3><p>风险等级: <span style="color:' + riskColors[riskLevel] + '; font-weight:bold;">' + city.risk_description + '</span></p>',
                            offset: new AMap.Pixel(0, -40)
                        });
                        
                        // 点击标记显示信息窗口
                        marker.on('click', function() {
                            infoWindow.open(map, marker.getPosition());
                        });
                    });
                } else {
                    console.error('城市风险数据格式错误:', cityRiskData);
                }
                
                console.log('地图初始化完成');
            };
        </script>
        <style>
            #container {width: 100%; height: 600px;}
        </style>
    </body>
    </html>
    """
    
    # 替换占位符
    map_html = map_html.replace('{api_key}', api_key)
    # 转换为JavaScript数组格式
    import json
    city_risk_json = json.dumps(city_risk_data)
    map_html = map_html.replace('{city_risk_data}', city_risk_json)
    
    return map_html