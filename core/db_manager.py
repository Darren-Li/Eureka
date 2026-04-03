import sqlite3
import json
import pandas as pd

DB_PATH = "data/analysis.db"

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def insert_dataset(data_dict):
    conn = get_conn()
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO datasets 
                 (name, file_path, row_count, col_count, columns_json, dtypes_json, 
                  missing_json, numeric_cols_json, categorical_cols_json, 
                  dataset_description, field_descriptions_json)
                 VALUES (?,?,?,?,?,?,?,?,?,?,?)''',
              (data_dict['name'], data_dict['file_path'], data_dict['row_count'],
               data_dict['col_count'], json.dumps(data_dict['columns']),
               json.dumps(data_dict['dtypes']), json.dumps(data_dict['missing_values']),
               json.dumps(data_dict['numeric_cols']), json.dumps(data_dict['categorical_cols']),
               data_dict.get('dataset_description',''),
               json.dumps(data_dict.get('field_descriptions',{}))))
    conn.commit()
    return c.lastrowid

def get_dataset(dataset_id):
    conn = get_conn()
    df = pd.read_sql_query(f"SELECT * FROM datasets WHERE id={dataset_id}", conn)
    conn.close()
    return df.iloc[0].to_dict() if not df.empty else None

def create_task(task_id, name, dataset_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO tasks (task_id, name, dataset_id) VALUES (?,?,?)", 
              (task_id, name, dataset_id))
    conn.commit()
    conn.close()

def get_task(task_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM tasks WHERE task_id=?", (task_id,))
    row = c.fetchone()
    if row:
        return dict(zip([desc[0] for desc in c.description], row))
    return None

def get_tasks():
    conn = get_conn()
    df = pd.read_sql_query("""
        SELECT t.*, d.name as dataset_name 
        FROM tasks t LEFT JOIN datasets d ON t.dataset_id = d.id 
        ORDER BY t.created_at DESC
    """, conn)
    conn.close()
    return df.to_dict('records') if not df.empty else []

def update_task_status(task_id, status, report_path=None, error=None):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""UPDATE tasks SET status=?, report_path=?, error_message=?, updated_at=CURRENT_TIMESTAMP 
                 WHERE task_id=?""", (status, report_path, error, task_id))
    conn.commit()
    conn.close()

def update_task_plan(task_id, plan, prompt):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""UPDATE tasks SET analysis_plan=?, user_prompt=?, updated_at=CURRENT_TIMESTAMP 
                 WHERE task_id=?""", (plan, prompt, task_id))
    conn.commit()
    conn.close()

def write_analysis_step(task_id, step_name, topic, idea, result, interpretation, chart_json=[]):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""INSERT INTO analysis_steps 
                 (task_id, step_name, analysis_topic, analysis_idea, analysis_result, 
                  analysis_interpretation, chart_json)
                 VALUES (?,?,?,?,?,?,?)""",
              (task_id, step_name, topic, idea, json.dumps(result) if isinstance(result, (dict,list)) else str(result),
               interpretation, str(chart_json)))
    conn.commit()
    conn.close()

def delete_analysis_step(task_id):
    conn = get_conn()
    c = conn.cursor()
    # 如果对应task_id存在分析记录，先删除
    c.execute("DELETE FROM analysis_steps WHERE task_id=?", (task_id,))
    conn.commit()
    conn.close()

def get_analysis_steps(task_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM analysis_steps WHERE task_id=? ORDER BY id", (task_id,))
    rows = c.fetchall()
    cols = [desc[0] for desc in c.description]
    return [dict(zip(cols, row)) for row in rows]