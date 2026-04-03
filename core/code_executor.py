import json
from core.db_manager import write_analysis_step
from core.llm_client import call_llm
import pandas as pd
import numpy as np
import os

def execute_code_with_ai(code, probe, task_id):
    # 预定义通用保存函数（适配任意分析场景）
    def save_analysis_step(step_name, topic, idea, result, chart_json=[]):
        # 统一数据格式
        if isinstance(result, (pd.DataFrame, pd.Series)):
            result = result.to_dict()
        elif not isinstance(result, (str, dict, list)):
            result = str(result)

        interp_prompt = f"""
        你是一位经验丰富、专业严谨的数据分析师，擅长从分析结果中提炼简洁、有洞察力的结论。

        ### 任务
        基于以下分析信息，生成一段高质量、专业简洁的解读结论。

        ### 输入信息
        - 主题：{topic}
        - 分析思路：{idea}
        - 分析结果：{result}
        - 图表信息：{chart_json if chart_json else "无图表"}

        ### 输出要求
        请严格按照以下结构输出，使用 Markdown 格式：

        1. **核心结论**  
           用1-3句话直接给出最重要、最有价值的发现或结论。语言要肯定、精炼，避免模棱两可。

        2. **数据洞察**  
           深入解释结果背后的含义，包括：
           - 关键数值或分布特征的意义
           - 可能的业务/数据含义（保持通用，不绑定具体行业）
           - 与预期或常规情况的对比（如果明显）
           - 值得注意的异常或模式

        ### 额外要求
        - 语言专业、客观、简洁有力，避免口语化和冗余话术（如“我们可以看出”“值得注意的是”等）。
        - 只输出以上两个部分（1 和 2），不要添加前言、总结、建议或其他无关内容。
        - 如果结果中包含图表信息（chart_json），请结合图表视觉特征进行解读，但不要直接描述代码。
        - 优先突出最具统计意义或最反直觉的发现。
        - 保持中性语气，基于数据说话，不夸大也不弱化结果。

        现在，请开始生成解读结论。
        """

        interpretation = call_llm(interp_prompt)
        write_analysis_step(task_id, step_name, topic, idea, result, interpretation, chart_json)
        return interpretation

    exec_env = {
        "pd": pd,
        "np": np,
        "os": os,
        "plt": __import__("matplotlib.pyplot"),  # 强制使用matplotlib
        "sns": __import__("seaborn"),            # 强制使用seaborn
        "json": json,

        "probe": probe,
        "df": pd.read_csv(probe["file_path"]) if probe["file_path"].endswith("csv") else pd.read_excel(probe["file_path"]),
        "task_id": task_id,
        "save_analysis_step": save_analysis_step
    }
    try:
        exec(code, 
            # {"__builtins__": {}}, 
            exec_env)
        return True, "执行成功"
    except Exception as e:
        return False, str(e)