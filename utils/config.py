# utils/config.py
import streamlit as st

def get_llm_config():
    """
    从 session_state 获取当前会话的 LLM 配置
    如果没有配置，返回 None 并让调用方处理
    """
    if "llm_config" not in st.session_state:
        return None
    
    return st.session_state.llm_config

def get_llm_code_config():
    """
    从 session_state 获取当前会话的 LLM 配置
    如果没有配置，返回 None 并让调用方处理
    """
    if "llm_code_config" not in st.session_state:
        return None
    
    return st.session_state.llm_code_config