import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

st.subheader('⚡ 电力供需风险预警（答辩核心亮点）')

# ====================== 步骤1：调用成员2的预测结果（自动衔接） ======================
if 'extreme_result' not in st.session_state:
    st.warning('⚠️ 请先去【预测页面】完成极端场景预测！')
    st.stop()

extreme_data = st.session_state['extreme_result']
df_clean = st.session_state['df_clean']

# ====================== 基础参数设置（可改这里的系统容量，贴合你们的课题） ======================
# 系统最大供电容量（可根据实际情况修改）
SYSTEM_CAPACITY = 1000  # 单位：MW

# ====================== 步骤2：风险等级判定 ======================
def calculate_risk_level(forecast_demand):
    """
    根据预测的电力负荷计算风险等级
    :param forecast_demand: 预测的电力负荷值（MW）
    :return: 风险等级和预警信息
    """
    if forecast_demand >= 0.9 * SYSTEM_CAPACITY:
        return "红色预警", "极高风险：电力供应严重不足，可能出现大面积停电！", "#FF4B4B"
    elif forecast_demand >= 0.75 * SYSTEM_CAPACITY:
        return "橙色预警", "高风险：电力供应紧张，需启动应急预案！", "#FFA500"
    elif forecast_demand >= 0.6 * SYSTEM_CAPACITY:
        return "黄色预警", "中等风险：电力供应偏紧，建议错峰用电！", "#FFFF00"
    else:
        return "绿色预警", "低风险：电力供应充足，无需采取措施。", "#4CAF50"

# 对预测数据进行风险判定
risk_results = []
for _, row in extreme_data.iterrows():
    level, message, color = calculate_risk_level(row['预测负荷'])
    risk_results.append({
        '时间': row['时间'],
        '预测负荷': row['预测负荷'],
        '风险等级': level,
        '预警信息': message,
        '颜色': color
    })

risk_df = pd.DataFrame(risk_results)

# ====================== 步骤3：风险预警弹窗和可视化 ======================
# 1. 显示风险预警表格
st.dataframe(risk_df[['时间', '预测负荷', '风险等级', '预警信息']], use_container_width=True)

# 2. 高亮显示最高风险等级
max_risk = risk_df['风险等级'].iloc[0]
max_risk_color = risk_df['颜色'].iloc[0]
st.markdown(f"""
    <div style="padding: 10px; border-radius: 5px; background-color: {max_risk_color}20; border-left: 5px solid {max_risk_color};">
        <h4>⚠️ 当前最高风险等级: {max_risk}</h4>
        <p>{risk_df['预警信息'].iloc[0]}</p>
    </div>
""", unsafe_allow_html=True)

# 3. 风险趋势可视化
st.subheader('📊 电力负荷与风险等级趋势')
fig, ax = plt.subplots(figsize=(12, 6))

# 绘制预测负荷曲线
ax.plot(risk_df['时间'], risk_df['预测负荷'], marker='o', linestyle='-', color='b', label='预测负荷')

# 添加风险等级阈值线
ax.axhline(y=0.9 * SYSTEM_CAPACITY, color='r', linestyle='--', label='红色预警阈值 (90%)')
ax.axhline(y=0.75 * SYSTEM_CAPACITY, color='orange', linestyle='--', label='橙色预警阈值 (75%)')
ax.axhline(y=0.6 * SYSTEM_CAPACITY, color='y', linestyle='--', label='黄色预警阈值 (60%)')

# 美化图表
ax.set_title('电力供需风险趋势预测', fontsize=16)
ax.set_xlabel('时间', fontsize=12)
ax.set_ylabel('预测负荷 (MW)', fontsize=12)
ax.legend()
ax.grid(True, linestyle='--', alpha=0.7)
plt.xticks(rotation=45)
plt.tight_layout()

# 在Streamlit中显示图表
st.pyplot(fig)

# 4. 风险详情弹窗
with st.expander("🔍 查看详细风险报告"):
    st.write("### 风险详情")
    for _, row in risk_df.iterrows():
        st.markdown(f"""
        <div style="margin: 5px 0; padding: 8px; border-radius: 3px; background-color: {row['颜色']}20;">
            <strong>时间:</strong> {row['时间']}<br>
            <strong>预测负荷:</strong> {row['预测负荷']:.2f} MW<br>
            <strong>风险等级:</strong> <span style="color: {row['颜色']};">{row['风险等级']}</span><br>
            <strong>预警信息:</strong> {row['预警信息']}
        </div>
        """, unsafe_allow_html=True)
