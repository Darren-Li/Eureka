import streamlit as st
from utils.file_handlers import save_uploaded_file
from core.data_probe import auto_probe
from core.db_manager import insert_dataset


st.set_page_config(layout="wide", page_icon="📁")
st.title("📁 数据管理")

uploaded = st.file_uploader("上传 CSV 或 Excel", type=["csv","xlsx"])
if uploaded:
    path = save_uploaded_file(uploaded)
    probe = auto_probe(path)
    with st.expander("数据集描述性统计：", expanded=True):
        st.json(probe)
    
    name = st.text_input("数据集名称", uploaded.name)
    desc = st.text_area("整体描述", height=50)

    with st.expander("字段描述：", expanded=True):
        col_widths = [1/2, 1, 3]
        header_cols = st.columns(col_widths)
        header_texts = ["序号", "字段名", "字段描述"]

        for col, text in zip(header_cols, header_texts):
            col.markdown(f"**{text}**")

        st.markdown('<hr style="margin:1px 0">', unsafe_allow_html=True)  # 表头分隔线

        field_desc = {}
        for idx, c in enumerate(probe["columns"], 1):
            cols = st.columns(col_widths)
            with cols[0]:
                st.write(idx)
            with cols[1]:
                st.write(c)
            with cols[2]:
                field_desc[c] = st.text_input("", placeholder="请输出字段描述和业务含义", key=c)
    
    if st.button("保存数据集", type="primary"):
        data = {**probe, "name": name, "dataset_description": desc, "field_descriptions": field_desc}
        ds_id = insert_dataset(data)
        st.success(f"保存成功！ID: {ds_id}")
