import streamlit as st
import os
import ast
from core.data_probe import auto_probe
from core.analysis_planner import generate_analysis_plan
from core.code_generator import generate_analysis_code
from core.code_executor import execute_code_with_ai
from core.report_generator import generate_professional_report
from core.db_manager import get_task, update_task_status, update_task_plan, get_dataset, get_analysis_steps, delete_analysis_step
from utils.file_handlers import delete_files_start_with


st.set_page_config(layout="wide", page_icon="🏃")
st.title("🚀 分析执行")

task_id = None
if "current_task_id" in st.session_state:
    task_id = st.session_state["current_task_id"]

if not task_id:
    st.error("请从任务管理页面进入")
    st.switch_page("pages/3_任务管理.py")
    st.stop()

task = get_task(task_id)
dataset = get_dataset(task['dataset_id'])
probe = auto_probe(dataset['file_path'], dataset['id'])

prompt = st.text_area("📝 输入分析要求（示例：分析各品类销售额分布、计算用户留存率、绘制相关性热力图）", 
    height=150,
    help="请描述你想要的分析内容、维度、图表类型等，例如：\n1. 统计各分类数据占比并绘制饼图\n2. 分析数值字段的相关性并绘制热力图\n3. 计算缺失值占比并给出处理建议"
    )

if st.button("开始全自动分析", type="primary"):
    update_task_status(task_id, "进行中")
    st.info(f"📌 任务ID：{task_id}（用于追踪分析记录）")

    with st.spinner("Step 1/4：生成分析计划..."):
        plan = generate_analysis_plan(probe, prompt)
        with st.expander("📋 Step1：分析计划", expanded=False):
            st.markdown(plan)
        update_task_plan(task_id, plan, prompt)

    try_cnt = 3
    error_text = ""
    while try_cnt > 0:
        try_cnt -= 1
        with st.spinner("Step 2/4：生成分析代码(Python)..."):
            code = generate_analysis_code(plan, probe, dataset['file_path'], task_id, error_text)

            # 保存代码
            code_path = os.path.join("temp", f"analysis_code_{task_id}.py")
            with open(code_path, "w", encoding="utf-8") as f:
                f.write(code)

            with st.expander("💻 Step2.1：分析代码", expanded=False):
                st.code(code, language="python")

        with st.spinner("🏃 Step2.2：执行分析代码..."):
            delete_analysis_step(task_id)
            delete_files_start_with("temp", f"{task_id}_")

            # 执行代码
            success, msg = execute_code_with_ai(code, probe, task_id)

        if success:
            st.success("分析执行完成！")
            break
        else:
            update_task_status(task_id, "分析执行失败", error=msg)
            st.error(msg)
            error_text = msg

            if try_cnt > 0:
                st.write("代码执行出错，重新生成后执行！（最多尝试3次）")
                continue
            else:
                st.stop()

    with st.spinner("Step 3/4：分析及总结..."):
        with st.expander("📊 Step3：分析过程和结论", expanded=False):
            records = get_analysis_steps(task_id)
            st.write(f"🔍 找到{len(records)}条分析记录：")
            for record in records:
                with st.expander(f"步骤：{record['step_name']}", expanded=False):
                    st.write(f"**分析主题**：{record['analysis_topic']}")
                    st.write(f"**分析思路**：{record['analysis_idea']}")
                    st.write(f"**分析结果**：")
                    st.code(record['analysis_result'], language="Python")
                    
                    chart_paths = ast.literal_eval(record["chart_json"])
                    if chart_paths:
                        for chart_path in chart_paths:
                            st.image(chart_path, caption=record['analysis_topic'], width=600)

                    st.write(f"**AI解读**：{record['analysis_interpretation']}")

    with st.spinner("Step 4/4：生成报告..."):
        with st.expander("📊 Step4：报告生成", expanded=False):
            report_path = generate_professional_report(task_id)
            update_task_status(task_id, "已完成", report_path)
            st.success("报告生成完成！")
            st.write(report_path)
            st.balloons()
