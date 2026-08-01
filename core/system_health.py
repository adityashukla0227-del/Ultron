import os
import platform
from datetime import datetime


def system_health():

    checks = {
        "Memory File": os.path.exists("data/memory.txt"),
        "Profile File": os.path.exists("data/profile.txt"),
        "Backup Folder": os.path.exists("backup"),
        "Logs Folder": os.path.exists("logs"),
        "Config File": os.path.exists("core/config.py"),
    }

    return checks



def system_summary():

    summary = {
        "OS": platform.system(),
        "OS Version": platform.version(),
        "Python Version": platform.python_version(),
        "Platform": platform.platform(),
        "Current Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Ultron Folder": os.getcwd()
    }

    return summary