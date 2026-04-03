import os
from pathlib import Path

def save_uploaded_file(uploaded_file):
    os.makedirs("data/uploads", exist_ok=True)
    file_path = os.path.join("data/uploads", uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def delete_files_start_with(folder, prefix):
    folder = Path(folder)
    if not folder.exists():
        print("文件夹不存在")
        return

    for f in folder.glob(f"{prefix}*"):
        if f.is_file():
            f.unlink()
            print(f"删除：{f.name}")
