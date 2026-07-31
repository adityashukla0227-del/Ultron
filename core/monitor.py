import os
import platform
from datetime import datetime

from core.logger import log_info


START_TIME = datetime.now()


def get_start_time():
    return START_TIME.strftime("%Y-%m-%d %H:%M:%S")


def get_system_info():
    return {
        "os": platform.system(),
        "os_version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor()
    }


def monitor_start():

    log_info("Ultron Started")

    print("\n===== ULTRON MONITOR =====")

    print(f"Start Time : {get_start_time()}")

    system = get_system_info()

    for key, value in system.items():
        print(f"{key.capitalize()} : {value}")

    print("==========================\n")

    return True



def monitor_shutdown():

    log_info("Ultron Shutdown")

    end_time = datetime.now()

    print("\n===== ULTRON SHUTDOWN =====")
    print(f"Shutdown Time : {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("===========================\n")

    return True



def check_module(module_name):

    status = False

    try:
        __import__(module_name)
        status = True

    except ImportError:
        status = False

    return {
        "module": module_name,
        "status": "Loaded" if status else "Failed"
    }



def system_status():

    return {
        "status": "Running",
        "uptime_start": get_start_time(),
        "python_version": platform.python_version()
    }