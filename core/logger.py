import os
from datetime import datetime

LOG_FILE = "data/logs.txt"


def create_log_file():
    if not os.path.exists("data"):
        os.makedirs("data")

    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as file:
            file.write("")


def save_log(level, message):
    create_log_file()

    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(LOG_FILE, "a") as file:
        file.write(f"[{time}] [{level}] {message}\n")


def log_info(message):
    save_log("INFO", message)


def log_warning(message):
    save_log("WARNING", message)


def log_error(message):
    save_log("ERROR", message)


def log_debug(message):
    save_log("DEBUG", message)


def get_logs():
    create_log_file()

    with open(LOG_FILE, "r") as file:
        logs = file.readlines()

    return logs


def clear_logs():
    create_log_file()

    with open(LOG_FILE, "w") as file:
        file.write("")

    return True