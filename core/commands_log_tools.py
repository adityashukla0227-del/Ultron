from core.logger import (
    clear_logs,
    search_logs
)


def handle_log_tools_commands(user):

    if user == "clear logs":

        clear_logs()

        print("\nUltron: All logs cleared successfully.\n")

        return True


    elif user.startswith("search logs "):

        keyword = user.replace("search logs ", "", 1).strip()

        logs = search_logs(keyword)

        if not logs:

            print("\nUltron: No matching logs found.\n")

        else:

            print("\n===== SEARCH RESULTS =====")

            for log in logs:

                print(log.strip())

            print("==========================\n")

        return True


    return False