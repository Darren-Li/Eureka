import pandas as pd
import numpy as np
from core.db_manager import get_dataset
import json
import os

def auto_probe(file_path: str, dataset_id=None):

    if os.path.exists(file_path):
            pass
    else:
        file_path = file_path.replace("\\", "/")

    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)
    
    probe = {
        "file_path": file_path,
        "row_count": len(df),
        "col_count": len(df.columns),
        "columns": df.columns.tolist(),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "missing_values": df.isnull().sum().to_dict(),
        "numeric_cols": df.select_dtypes(include=[np.number]).columns.tolist(),
        "categorical_cols": df.select_dtypes(include=['object','category']).columns.tolist(),
        "sample_data": df.head(3).to_dict('records')
    }
    
    if dataset_id:
        ds = get_dataset(dataset_id)
        probe["field_descriptions"] = json.loads(ds.get('field_descriptions_json','{}')) if ds else {}
    else:
        probe["field_descriptions"] = {}
    
    return probe