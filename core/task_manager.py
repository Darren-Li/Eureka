import uuid
from core.db_manager import create_task

def create_new_task(name, dataset_id):
    task_id = f"task_{uuid.uuid4().hex[:12]}"
    create_task(task_id, name, dataset_id)
    return task_id