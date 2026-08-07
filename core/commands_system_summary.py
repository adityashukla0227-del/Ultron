from core.system_health import system_summary


def handle_system_summary_commands(user):

    if user == "system summary":

        summary = system_summary()

        print("\n===== SYSTEM SUMMARY =====")

        for key, value in summary.items():

            print(f"{key.capitalize()} : {value}")

        print("==========================\n")

        return True

    return False