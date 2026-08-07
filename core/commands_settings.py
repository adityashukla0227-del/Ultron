from core.settings import (
    show_settings,
    update_setting,
    reset_settings
)


def handle_settings_commands(user):

    if user == "show settings":

        settings = show_settings()

        print("\n===== SETTINGS =====")

        for key, value in settings.items():

            print(f"{key} : {value}")

        print("====================\n")

        return True


    elif user.startswith("set "):

        parts = user.split(" ", 2)

        if len(parts) < 3:

            print("\nUltron: Usage -> set KEY VALUE\n")

            return True

        key = parts[1]

        value = parts[2]

        update_setting(key, value)

        print("\nUltron: Setting updated successfully.\n")

        return True


    elif user == "reset settings":

        reset_settings()

        print("\nUltron: Settings reset successfully.\n")

        return True


    return False