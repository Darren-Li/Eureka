import streamlit as st
from database.schema import init_db


# ==================== 数据库初始化（只执行一次） ====================
if "db_initialized" not in st.session_state:
    init_db()
    st.session_state.db_initialized = True
    st.toast("✅ 数据库初始化完成", icon="✅")

st.set_page_config(
    page_title="Eureka",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.header("🤖 Eureka - An Agentic Analytics Platform")
st.markdown("")
st.subheader("在这里！只要说出你的要求和思路，分析和洞察随之而来。让数据驱动决策，从今天开始！")
st.markdown("")

st.markdown(
    """
    <div style="text-align: center; margin-top: 50px; color: gray; font-size: 16px;">
        Copyright©2026 南京秉智数据科技有限公司
    </div>
    """,
    unsafe_allow_html=True
)
