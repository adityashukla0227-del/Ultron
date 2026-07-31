import os
import shutil

EXPORT_FOLDER = "exports"

EXPORT_FILES = {
    "memories": os.path.join(EXPORT_FOLDER, "memory.txt"),
    "profile": os.path.join(EXPORT_FOLDER, "profile.txt")
}

DATA_FILES = {
    "memories": "data/memory.txt",
    "profile": "data/profile.txt"
}


def import_memories():
    if os.path.exists(EXPORT_FILES["memories"]):
        shutil.copy(EXPORT_FILES["memories"], DATA_FILES["memories"])
        return True

    return False


def import_profile():
    if os.path.exists(EXPORT_FILES["profile"]):
        shutil.copy(EXPORT_FILES["profile"], DATA_FILES["profile"])
        return True

    return False


def import_all():
    imported = 0

    if import_memories():
        imported += 1

    if import_profile():
        imported += 1

    return imported == 2