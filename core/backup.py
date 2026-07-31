import shutil
import os
from datetime import datetime

BACKUP_FOLDER = "backup"

FILES_TO_BACKUP = [
    "data/memory.txt",
    "data/profile.txt"
]


def create_backup():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    backup_path = os.path.join(BACKUP_FOLDER, timestamp)

    os.makedirs(backup_path, exist_ok=True)

    copied_files = 0

    for file in FILES_TO_BACKUP:
        if os.path.exists(file):
            shutil.copy(file, backup_path)
            copied_files += 1

    return copied_files > 0