from core.profile import get_all_profiles


def handle_profile_commands(user):
    if user == "who am i":

        profile = get_all_profiles()

        if not profile:
            print("\nUltron: No profile information found.\n")

        else:
            print("\n===== USER PROFILE =====")

            for key, value in profile.items():
                print(f"{key.capitalize()} : {value}")

            print("========================\n")

        return True

    return False