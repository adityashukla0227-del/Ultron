import os
import shutil

BACKUP_FOLDER = "backup"

FILES_TO_RESTORE = [
    "memory.txt",
    "profile.txt"
]


def restore_backup(backup_name):

    backup_path = os.path.join(BACKUP_FOLDER, backup_name)

    if not os.path.exists(backup_path):
        return False

    os.makedirs("data", exist_ok=True)

    for file in FILES_TO_RESTORE:
        source = os.path.join(backup_path, file)
        destination = os.path.join("data", file)

        if os.path.exists(source):
            shutil.copy(source, destination)

    return True