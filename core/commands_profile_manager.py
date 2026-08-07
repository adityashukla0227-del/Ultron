from core.profile_manager import (
    show_profile,
    set_profile,
    delete_profile,
    reset_profile
)


def handle_profile_manager_commands(user):

    if user == "profile show":

        profile = show_profile()

        print("\n===== PROFILE DATA =====")

        if not profile:
            print("No profile data found.")
        else:
            for key, value in profile.items():
                print(f"{key} : {value}")

        print("========================\n")

        return True

    elif user.startswith("profile set "):

        parts = user.split(" ", 3)

        if len(parts) < 4:
            print("\nUltron: Usage -> profile set KEY VALUE\n")
            return True

        key = parts[2]
        value = parts[3]

        set_profile(key, value)

        print("\nUltron: Profile updated successfully.\n")

        return True

    elif user.startswith("profile delete "):

        key = user.replace("profile delete ", "", 1).strip()

        if delete_profile(key):
            print("\nUltron: Profile data deleted successfully.\n")
        else:
            print("\nUltron: Profile key not found.\n")

        return True

    elif user == "profile reset":

        reset_profile()

        print("\nUltron: Profile reset successfully.\n")

        return True

    return False