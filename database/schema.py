import sqlite3
import os

DB_PATH = "data/analysis.db"

def init_db():
    os.makedirs("data/uploads", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 数据集表
    c.execute('''CREATE TABLE IF NOT EXISTS datasets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        file_path TEXT NOT NULL UNIQUE,
        row_count INTEGER,
        col_count INTEGER,
        columns_json TEXT,
        dtypes_json TEXT,
        missing_json TEXT,
        numeric_cols_json TEXT,
        categorical_cols_json TEXT,
        dataset_description TEXT,
        field_descriptions_json TEXT,
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # 任务表
    c.execute('''CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        dataset_id INTEGER NOT NULL,
        user_prompt TEXT,
        analysis_plan TEXT,
        status TEXT DEFAULT '未开始',
        report_path TEXT,
        error_message TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (dataset_id) REFERENCES datasets(id)
    )''')
    
    # 分析步骤表
    c.execute('''CREATE TABLE IF NOT EXISTS analysis_steps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id TEXT NOT NULL,
        step_name TEXT,
        analysis_topic TEXT,
        analysis_idea TEXT,
        analysis_result TEXT,
        analysis_interpretation TEXT,
        chart_json TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (task_id) REFERENCES tasks(task_id)
    )''')
    
    conn.commit()
    conn.close()
    print("✅ 数据库表全部创建完成")