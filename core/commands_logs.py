from core.logger import get_logs


def handle_logs_commands(user):
    if user == "show logs":

        logs = get_logs()

        if not logs:
            print("\nUltron: No logs found.\n")

        else:
            print("\n========== LOGS ==========")

            for log in logs:
                print(log.strip())

            print("==========================\n")

        return True

    return False