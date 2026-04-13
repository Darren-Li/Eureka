from core.llm_client import call_llm_code
from core.db_manager import get_task, get_analysis_steps
import ast
import streamlit as st
import base64


def generate_professional_report(task_id):
    task = get_task(task_id)
    steps = get_analysis_steps(task_id)
    
    context = f"用户提示: {task['user_prompt']} \n计划: {task['analysis_plan']} \n步骤: {steps}"

    # 通用报告生成提示（无场景绑定）
    report_prompt = f"""
    你是一名资深数据分析师 + 前端工程师，请基于分析记录生成一个**专业、完整、可运行的HTML分析报告**。

    ==================
    【输入信息】
    {context}
    ==================

    【核心任务】
    1. 先理解用户分析需求
    2. 总结分析过程与关键结论
    3. 生成结构化、专业、美观的HTML报告

    ==================
    【强制规范（必须严格遵守）】

    【1. 输出格式】
    - 只能输出 HTML 代码
    - 不允许出现任何解释、markdown、```html 等
    - HTML必须完整：
      - 开头：<!DOCTYPE html>
      - 结尾：</html>
    - 必须包含：
      <html>
      <head>
      <style>
      <body>
      <script>

    ------------------

    【2. 页面结构（必须完整实现）】

    页面必须包含以下模块（缺一不可）：

    ① 标题区
    - 自动生成报告标题（基于用户需求）
    - 以1.,2.等数字为编号，以此显示标题

    ② 数据概览
    - 数据行数
    - 列数
    - 字段类型（表格形式）

    ③ 左侧目录（固定侧边栏）
    - 每个分析步骤一个目录项
    - 点击可跳转（锚点）
    - 当前选中高亮

    ④ 分析步骤区（核心内容）
    每个步骤必须包含：
    - 标题（步骤名称）
    - 分析主题
    - 分析思路
    - 分析结论（重点突出）
    - 图表区域（如有）

    ⑤ 总体结论
    - 汇总所有步骤结论
    - 给出整体洞察

    ⑥ 页脚
    - 生成时间

    ------------------

    【3. 图表渲染（关键约束）】

    对每个分析步骤 record：

    - 遍历 record.chart_json
    - 严格使用以下占位符（不能修改）：

    {{{{chart_${{record['id']}}_0}}}}
    {{{{chart_${{record['id']}}_1}}}}
    ...

    HTML结构必须为：

    <div class="chart-container">
        <img src="data:image/png;base64,{{{{chart_${{record['id']}}_${{idx}}}}}}" class="chart-img" width="600" height="400" alt="{{{{record.analysis_topic}}}}">
    </div>

    规则：
    - idx 每个 record 从 0 递增
    - chart_json 为空 → 不生成该模块
    - 图片必须自适应宽度

    ------------------

    【4. CSS要求】

    - 使用原生CSS（禁止Tailwind）
    - 风格：商务 / 数据分析报告风格
    - 必须实现：
      - 左侧固定目录（position: fixed）
      - 主内容右侧布局
      - 卡片式内容（box-shadow + 圆角）
      - 响应式（宽屏 / 窄屏可用）

    ------------------

    【5. 交互功能（必须实现）】

    必须用原生JS实现：

    ① 目录锚点跳转
    ② 当前目录高亮
    ③ 图片点击放大（modal弹层）
    ④ 回到顶部按钮

    ------------------

    【6. 内容生成要求】

    - 内容必须基于分析记录真实生成（禁止空话）
    - 每个步骤：
      - 思路：解释做了什么分析
      - 结论：明确结果（有业务价值）

    ------------------

    【7. 代码质量要求】

    - HTML结构清晰、标签闭合完整
    - CSS类名语义化（如：sidebar, content, card）
    - JS可直接运行（不能伪代码）

    ------------------

    【8. 严格禁止】

    - 外部依赖（CDN / JS库）
    - 虚构字段 / 虚构数据
    - 修改占位符格式
    - 输出非HTML内容

    ==================

    请生成最终HTML。
    """

    html_content = call_llm_code(report_prompt)
   
    for record in steps:
        chart_paths = ast.literal_eval(record["chart_json"])
        if chart_paths:
            for idx, img_path in enumerate(chart_paths):
                try:
                    # 处理图表base64
                    with open(img_path, "rb") as f:
                        b64_encoded = base64.b64encode(f.read()).decode("utf-8")
                    placeholder = f"{{{{chart_{record['id']}_{idx}}}}}"
                    html_content = html_content.replace(placeholder, b64_encoded)
                except Exception as e:
                    st.warning(f"⚠️ 处理图表 {img_path} 失败：{str(e)}")
                    default_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
                    placeholder = f"{{{{chart_{record['id']}_{idx}}}}}"
                    html_content = html_content.replace(placeholder, default_b64)
    
    path = f"reports/Analysis_Report_{task_id}.html"
    with open(path, "w", encoding="utf-8") as f:
        f.write(html_content)
    return path