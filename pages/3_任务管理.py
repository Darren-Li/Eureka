import streamlit as st
import os
import pandas as pd
import sqlite3
from core.task_manager import create_new_task
from core.db_manager import get_tasks, update_task_status


st.set_page_config(layout="wide", page_icon="📋")
st.title("📋 任务管理")

# ==================== 创建任务 ====================
st.subheader("➕ 创建新任务")
conn = sqlite3.connect("data/analysis.db")
ds_list = pd.read_sql("SELECT id, name FROM datasets", conn)
conn.close()

if ds_list.empty:
    st.info("请先去「数据管理」上传数据集")
else:
    col1, col2 = st.columns([2,3])
    ds_id = col1.selectbox("选择数据集", ds_list['id'], format_func=lambda x: ds_list[ds_list['id']==x]['name'].iloc[0])
    task_name = col2.text_input("任务名称")
    
    if st.button("创建任务", type="primary"):
        if task_name:
            task_id = create_new_task(task_name, ds_id)
            st.success(f"任务 {task_id} 创建成功！")
            st.rerun()

# ==================== 任务列表 ====================
st.subheader("我的任务")
tasks = get_tasks()

if not tasks:
    st.info("还没有任务")
else:
    for task in tasks:
        spaces = "&nbsp;" * 10
        with st.expander(f"{task['name']}{spaces}状态：**{task['status']}**"):
            c1, c2, c3, c4 = st.columns([3,2,1,1])
            with c1:
                st.write(f"任务ID：{task['task_id']}")
                st.write(f"数据集：{task.get('dataset_name')}")
            with c2:
                st.write(f"创建时间：{task['created_at']}")
                st.write(f"更新时间：{task['updated_at']}")
            
            if c3.button("▶️ 进入分析", key=f"ana_{task['task_id']}"):
                # 2. 核心：将任务ID存入session_state（跨页面共享）
                st.session_state["current_task_id"] = task['task_id']  # 自定义key，如current_task_id
                st.switch_page("pages/4_分析执行.py")
                
            if task['status'] == "已完成" and task.get('report_path'):
                report_file = task['report_path']

                # 检查文件物理路径是否存在
                if os.path.exists(report_file):
                    with open(report_file, "rb") as f:
                        c4.download_button(
                            label="⬇️ 下载报告",
                            data=f,
                            file_name=f"报告_{task['name']}.html",
                            mime="text/html",
                            key=f"key_{task['task_id']}"
                        )
                else:
                    # 如果文件不存在，在对应的列或容器中显示警告
                    c4.warning("⚠️ 报告文件丢失，请重新执行分析")
