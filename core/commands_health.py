from core.system_health import system_health


def handle_health_commands(user):

    if user == "system health":

        health = system_health()

        print("\n===== SYSTEM HEALTH =====")

        for key, value in health.items():
            print(f"{key.capitalize()} : {value}")

        print("=========================\n")

        return True

    return False