from openai import OpenAI
import streamlit as st

# 调用 zhipu 模型
from zai import ZhipuAiClient
from utils.config import get_llm_config, get_llm_code_config


def _call_llm_internal(config, prompt: str, temperature=None) -> str:
    """内部核心调用函数（避免重复代码）"""
    if config is None or not config.get("api_key"):
        st.error("⚠️ 大模型未配置或 API Key 无效")
        st.warning("请前往「模型配置」页面完成设置")
        st.stop()

    try:
        # 处理特殊供应商
        if config["provider"] == "zhipu":
            client = ZhipuAiClient(api_key=config["api_key"])
        else:
            client = OpenAI(
                api_key=config["api_key"],
                base_url=config.get("base_url")
            )

        resp = client.chat.completions.create(
            model=config["model"],
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature or config.get("temperature", 0.3)
        )
        return resp.choices[0].message.content.strip()

    except Exception as e:
        st.error(f"调用大模型失败：{str(e)}")
        st.info("可能原因：API Key 错误、网络问题、模型名称不对。请返回「模型配置」页面检查并重新测试。")
        st.stop()


# ====================== 对外暴露的简洁接口 ======================
def call_llm(prompt: str, temperature=None) -> str:
    """通用模型调用"""
    config = get_llm_config()
    return _call_llm_internal(config, prompt, temperature)


def call_llm_code(prompt: str, temperature=None) -> str:
    """编程专用模型调用（可使用不同配置）"""
    config = get_llm_code_config()
    code_text = _call_llm_internal(config, prompt, temperature)
    # 移除开头的标记
    code_text = code_text.replace("```python", "").replace("```py", "").replace("```", "")
    # 移除结尾的标记并去除两端空格
    return code_text.strip()


# # Azure AI Inference SDK方式调用github模型
# from azure.ai.inference import ChatCompletionsClient
# from azure.ai.inference.models import SystemMessage, UserMessage
# from azure.core.credentials import AzureKeyCredential

# def call_llm_github(prompt: str, temperature=None) -> str:
#     config = get_llm_config()
    
#     if config is None or not config.get("api_key"):
#         st.error("⚠️ 大模型未配置或 API Key 无效")
#         st.warning("请前往「模型配置」页面完成设置")
#         st.stop()  # 直接中断执行，强制用户去配置
    
#     try:
#         client = ChatCompletionsClient(
#             endpoint=config.get("base_url"),
#             credential=config["api_key"]
#         )

        
#         resp = client.complete(
#             model=config["model"],
#             messages=[
#                 SystemMessage(content="You are a helpful, accurate, and concise assistant."),
#                 UserMessage(content=prompt)
#                 ],
#             temperature=temperature or config.get("temperature", 0.3),
#             top_p=0.9,
#             max_tokens=500,
#         )
#         return resp.choices[0].message.content.strip()
    
#     except Exception as e:
#         st.error(f"调用大模型失败：{str(e)}")
#         st.info("可能原因：API Key 错误、网络问题、模型名称不对。请返回「模型配置」页面检查并重新测试。")
#         st.stop()
