import os

SETTINGS_FILE = "data/settings.txt"

DEFAULT_SETTINGS = {
    "theme": "dark",
    "username": "User",
    "assistant": "Ultron",
    "autosave": "true"
}


def create_settings():
    if not os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "w") as file:
            for key, value in DEFAULT_SETTINGS.items():
                file.write(f"{key}={value}\n")


def load_settings():
    create_settings()

    settings = {}

    with open(SETTINGS_FILE, "r") as file:
        for line in file:
            if "=" in line:
                key, value = line.strip().split("=", 1)
                settings[key] = value

    return settings


def save_settings(settings):
    with open(SETTINGS_FILE, "w") as file:
        for key, value in settings.items():
            file.write(f"{key}={value}\n")


def update_setting(key, value):
    settings = load_settings()

    settings[key] = value

    save_settings(settings)

    return True


def reset_settings():
    save_settings(DEFAULT_SETTINGS)
    return True


def get_setting(key):
    settings = load_settings()

    return settings.get(key)


def show_settings():
    return load_settings()