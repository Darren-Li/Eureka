import streamlit as st
from core.llm_client import call_llm, call_llm_code

st.set_page_config(layout="wide", page_icon="🧠")
st.title("🔧 模型配置")
st.markdown("请在此页面设置大模型参数，配置成功后即可使用分析功能。")
st.caption("配置仅保存在当前会话中，关闭浏览器后需重新设置。")

# ==================== 供应商模型定义（保持不变）====================
PROVIDER_MODELS = {
    "openai": {"models": ["gpt-3.5-turbo", "gpt-4", "gpt-4o"], "base_url": None},
    "github": {
        "models": ["openai/gpt-4.1", "openai/gpt-4o", "openai/gpt-4o-mini", "openai/gpt-5",
                   "deepseek/DeepSeek-V3-0324", "xai/gork-3"],
        "base_url": "https://models.github.ai/inference"
    },
    "openrouter": {
        "models": ["qwen/qwen3-next-80b-a3b-instruct:free", "qwen/qwen3-coder:free", 
                   "z-ai/glm-4.5-air:free",
                   "meta-llama/llama-3.3-70b-instruct:free",
                   "minimax/minimax-m2.5:free", 
                   "google/gemma-3-27b-it:free",
                   "nvidia/nemotron-3-super-120b-a12b:free",
                   "google/gemma-4-31b-it:free",
                   ],
        "base_url": "https://openrouter.ai/api/v1"
    },
    "aliyun": {
        "models": ["qwen3.6-plus", "qwen3.5-122b-a10b", "qwen3.5-397b-a17b",
                   "qwen3.5-flash", "qwen3.5-flash-2026-02-23", "qwen3.5-35b-a3b",
                   "qwen3-coder-next", "qwen3-max-2026-01-23",
                   "glm-5", "kimi-k2.5", "MiniMax-M2.5"],
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"
    },
    "xiaomi": {
        "models": ["mimo-v2-pro", "mimo-v2-omni", "mimo-v2-flash"],
        "base_url": "https://open.bigmodel.cn/api/paas/v4"
    },
    "zhipu": {
        "models": ["glm-4.7-flash", "glm-4-flash", "glm-4-flash-250414", "glm-4.6v-flash"],
        "base_url": "https://open.bigmodel.cn/api/paas/v4"
    },
}


# ==================== 通用配置 Tab 渲染函数（核心简化点）====================
def render_config_tab(config_key: str, test_func: callable):
    """渲染一个模型配置 Tab"""
    if config_key not in st.session_state:
        st.session_state[config_key] = {
            "provider": "aliyun",
            "model": "qwen3.5-flash",
            "api_key": "",
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "temperature": 0.3
        }

    current = st.session_state[config_key]
    provider_options = list(PROVIDER_MODELS.keys())

    cols = st.columns([1, 2])

    # ---------------- 左侧 ----------------
    with cols[0]:
        provider = st.selectbox(
            "供应商",
            options=provider_options,
            index=provider_options.index(current["provider"]),
            key=f"provider_{config_key}"
        )

        # 切换供应商时自动更新 model 和 base_url
        if provider != current["provider"]:
            st.session_state[config_key]["provider"] = provider
            st.session_state[config_key]["model"] = PROVIDER_MODELS[provider]["models"][0]
            st.session_state[config_key]["base_url"] = PROVIDER_MODELS[provider]["base_url"]
            st.rerun()

        base_url = st.text_input(
            "Base URL",
            value=current["base_url"] or "",          # 防止 None 显示问题
            placeholder="https://api.openai.com/v1  或留空使用默认",
            help="大多数供应商需要填写，OpenAI官方可留空",
            key=f"base_url_{config_key}_{current["provider"]}"
        )

    # ---------------- 右侧 ----------------
    with cols[1]:
        models = PROVIDER_MODELS[provider]["models"]
        model_name = st.selectbox(
            "模型名称",
            options=models,
            index=models.index(current["model"]) if current["model"] in models else 0,
            key=f"model_{config_key}"
        )

        api_key = st.text_input(
            "API Key",
            value=current["api_key"],
            type="password",
            key=f"pw_{config_key}"
        )

    temperature = st.slider(
        "Temperature", 0.0, 1.0, current["temperature"], 0.05,
        key=f"temp_{config_key}"
    )

    # ---------------- 保存 & 测试 ----------------
    if st.button("保存配置并测试", type="primary", key=f"submit_{config_key}"):
        if not api_key.strip():
            st.error("API Key 不能为空")
            return

        # 保存配置
        st.session_state[config_key] = {
            "provider": provider,
            "model": model_name,
            "api_key": api_key,
            "base_url": base_url.strip() or None,
            "temperature": temperature
        }

        st.success("配置已保存到当前会话！")

        # 测试连接
        with st.spinner("正在测试连接..."):
            try:
                response = test_func("请只回复四个字：连接成功", temperature=0.0)
                if "连接成功" in response:
                    st.balloons()
                    st.success("测试成功！大模型连接正常。")
                else:
                    st.warning("调用成功但回复异常，请检查模型是否正常。")
            except Exception as e:
                st.error(f"测试失败：{str(e)}")
                st.info("可能原因：API Key 错误、模型名不对、网络问题、供应商配置错误。")

    # ---------------- 显示当前配置 ----------------
    if config_key in st.session_state:
        show_config = st.session_state[config_key].copy()
        show_config["api_key"] = "••••" + show_config["api_key"][-4:] if show_config["api_key"] else "未设置"
        st.markdown("**当前会话模型配置：**")
        st.json(show_config)


# ==================== 主界面 ====================
tab1, tab2 = st.tabs(["🧠 通用模型", "💻 编程模型"])

with tab1:
    render_config_tab(config_key="llm_config", test_func=call_llm)

with tab2:
    render_config_tab(config_key="llm_code_config", test_func=call_llm_code)