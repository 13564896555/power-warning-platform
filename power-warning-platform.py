import streamlit as st

# 设置页面配置（必须放在最前面）
st.set_page_config(
    page_title="电力预警平台",
    page_icon="⚡",
    layout="wide"
)

# 定义侧边栏导航
st.sidebar.title("⚡ 电力预警平台")
page = st.sidebar.radio(
    "选择功能模块",
    ["数据上传与可视化", "负荷预测", "风险预警"]
)

# 根据选择加载不同页面
if page == "数据上传与可视化":
    # 导入并运行你的 data_page.py 模块
    exec(open("data_page.py", encoding="utf-8").read())

elif page == "负荷预测":
    st.subheader("🔮 负荷预测模块")
    st.info("此模块由成员二负责开发")

elif page == "风险预警":
    st.subheader("⚠️ 风险预警模块")
    st.info("此模块由成员三负责开发")

# 页脚
st.sidebar.markdown("---")
st.sidebar.markdown("📌 合肥工业大学大创项目")