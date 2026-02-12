import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 中文显示设置
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 页面标题
st.subheader('📊 数据上传与可视化界面')

# 1. 数据上传组件（界面核心）
uploaded_file = st.file_uploader('请上传Excel/CSV格式数据（含日期、气温、风速、负荷、出力等列）', type=['xlsx', 'csv'])

# 全局变量存清洗后的数据（给其他页面传值，仅界面衔接）
if 'df_clean' not in st.session_state:
    st.session_state.df_clean = None

if uploaded_file is not None:
    # 读取文件（界面功能）
    if uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file)

    st.success('✅ 数据上传成功！')
    st.write('原始数据预览（前5行）：')
    st.dataframe(df.head(), use_container_width=True)

    # 2. 自动数据清洗（纯界面流程，无算法）
    st.write('---')
    st.subheader('✅ 自动数据清洗')
    with st.spinner('正在清洗数据...'):
        # 日期格式统一（界面展示用）
        if 'datetime' in df.columns:
            df['datetime'] = pd.to_datetime(df['datetime'])
            df = df.set_index('datetime')
        else:
            st.error('❌ 数据缺少datetime列！请补充后上传')
            st.stop()

        # 删空值、异常值（界面数据整理，无复杂计算）
        df = df.dropna()

        def remove_outliers(data, col):
            q1 = data[col].quantile(0.25)
            q3 = data[col].quantile(0.75)
            iqr = q3 - q1
            lower = q1 - 1.5*iqr
            upper = q3 + 1.5*iqr
            return data[(data[col]>=lower) & (data[col]<=upper)]

        clean_cols = ['temp', 'wind_speed', 'power_load', 'thermal_power', 'wind_power', 'pv_power']
        for col in clean_cols:
            if col in df.columns:
                df = remove_outliers(df, col)

        # 计算总供电、供需缺口（界面展示用，简单加减）
        df['total_power'] = df['thermal_power'] + df['wind_power'] + df['pv_power']
        df['supply_demand_gap'] = df['total_power'] - df['power_load']

        st.session_state.df_clean = df.reset_index()

    st.success(f'✅ 数据清洗完成！清洗后共 {len(st.session_state.df_clean)} 行')
    st.write('清洗后数据预览：')
    st.dataframe(st.session_state.df_clean.head(), use_container_width=True)

    # 3. 数据可视化图表（纯界面展示，无算法）
    st.write('---')
    st.subheader('📈 数据可视化展示')
    df_viz = st.session_state.df_clean

    # 气温+负荷趋势图（界面核心图表）
    fig1, ax1 = plt.subplots(figsize=(10, 4))
    ax1_twin = ax1.twinx()
    ax1.plot(df_viz['datetime'], df_viz['temp'], color='red', label='气温', linewidth=2)
    ax1_twin.plot(df_viz['datetime'], df_viz['power_load'], color='blue', label='用电负荷', linewidth=2)

    ax1.set_xlabel('日期')
    ax1.set_ylabel('气温', color='red')
    ax1_twin.set_ylabel('用电负荷', color='blue')
    ax1.legend(loc='upper left')
    ax1_twin.legend(loc='upper right')
    st.pyplot(fig1)

    # 供需缺口分布直方图（界面补充图表）
    fig2, ax2 = plt.subplots(figsize=(8, 4))
    ax2.hist(df_viz['supply_demand_gap'], bins=20, color='green', alpha=0.7)
    ax2.set_xlabel('供需缺口（正=供大于求，负=缺电）')
    ax2.set_ylabel('频次')
    ax2.axvline(0, color='red', linestyle='--', label='供需平衡线')
    ax2.legend()
    st.pyplot(fig2)

else:
    st.info('💡 请先上传数据文件，解锁后续功能')

# 界面底部提示（优化体验）
st.write('---')
st.markdown('📌 操作说明：上传数据 → 自动清洗 → 查看可视化图表 → 进入「预测界面」')
