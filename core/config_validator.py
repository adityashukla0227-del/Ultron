import os

from core.config import (
    APP_NAME,
    VERSION,
    DEVELOPER,
    STATUS
)


def validate_config():

    checks = {
        "APP_NAME": bool(APP_NAME),
        "VERSION": bool(VERSION),
        "DEVELOPER": bool(DEVELOPER),
        "STATUS": bool(STATUS),

        "Data Folder": os.path.exists("data"),
        "Backup Folder": os.path.exists("backup"),
        "Export Folder": os.path.exists("exports"),
        "Config File": os.path.exists("core/config.py")
    }

    return checks



def config_summary():

    summary = {
        "Application": APP_NAME,
        "Version": VERSION,
        "Developer": DEVELOPER,
        "Status": STATUS
    }

    return summary