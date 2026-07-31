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


def list_backups():
    if not os.path.exists(BACKUP_FOLDER):
        return []

    backups = []

    for item in os.listdir(BACKUP_FOLDER):
        path = os.path.join(BACKUP_FOLDER, item)
        if os.path.isdir(path):
            backups.append(item)

    backups.sort(reverse=True)
    return backups


def latest_backup():
    backups = list_backups()

    if backups:
        return backups[0]

    return None


def backup_count():
    return len(list_backups())


def delete_backup(name):
    backup_path = os.path.join(BACKUP_FOLDER, name)

    if os.path.exists(backup_path):
        shutil.rmtree(backup_path)
        return True

    return False


def backup_info(name):
    backup_path = os.path.join(BACKUP_FOLDER, name)

    if not os.path.exists(backup_path):
        return None

    files = []

    for file in os.listdir(backup_path):
        files.append(file)

    return files