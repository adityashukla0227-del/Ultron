import os
import shutil

EXPORT_FOLDER = "exports"

FILES_TO_EXPORT = {
    "memories": "data/memory.txt",
    "profile": "data/profile.txt"
}


def export_memories():
    os.makedirs(EXPORT_FOLDER, exist_ok=True)

    if os.path.exists(FILES_TO_EXPORT["memories"]):
        shutil.copy(FILES_TO_EXPORT["memories"], EXPORT_FOLDER)
        return True

    return False


def export_profile():
    os.makedirs(EXPORT_FOLDER, exist_ok=True)

    if os.path.exists(FILES_TO_EXPORT["profile"]):
        shutil.copy(FILES_TO_EXPORT["profile"], EXPORT_FOLDER)
        return True

    return False


def export_all():
    exported = 0

    if export_memories():
        exported += 1

    if export_profile():
        exported += 1

    return exported == 2