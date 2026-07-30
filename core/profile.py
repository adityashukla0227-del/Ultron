PROFILE_FILE = "data/profile.txt"


def save_profile(key, value):
    profile = {}

    try:
        with open(PROFILE_FILE, "r") as file:
            for line in file:
                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    profile[k] = v
    except FileNotFoundError:
        pass

    profile[key] = value

    with open(PROFILE_FILE, "w") as file:
        for k, v in profile.items():
            file.write(f"{k}={v}\n")


def get_profile(key):
    try:
        with open(PROFILE_FILE, "r") as file:
            for line in file:
                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    if k == key:
                        return v
    except FileNotFoundError:
        pass

    return None