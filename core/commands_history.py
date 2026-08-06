from core.history import get_history


def handle_history_commands(user):
    if user == "history":

        history = get_history()

        if not history:
            print("\nUltron: No command history found.\n")

        else:
            print("\n===== COMMAND HISTORY =====")

            for index, command in enumerate(history, start=1):
                print(f"{index}. {command}")

            print("===========================\n")

        return True

    return False