import os

PROFILE_FILE = "data/profile.txt"


def load_profile():
    profile = {}

    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, "r") as file:
            for line in file:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    profile[key] = value

    return profile


def save_profile_data(profile):
    with open(PROFILE_FILE, "w") as file:
        for key, value in profile.items():
            file.write(f"{key}={value}\n")


def show_profile():
    return load_profile()


def set_profile(key, value):
    profile = load_profile()

    profile[key] = value

    save_profile_data(profile)

    return True


def delete_profile(key):
    profile = load_profile()

    if key in profile:
        del profile[key]
        save_profile_data(profile)
        return True

    return False


def reset_profile():
    with open(PROFILE_FILE, "w") as file:
        file.write("")

    return True