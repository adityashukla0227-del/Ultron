import os

from core.config import APP_NAME, VERSION, DEVELOPER, STATUS


def handle_system_commands(user):

    if user == "help":

        print("\n========== COMMANDS ==========")
        print("help                  - Show all commands")
        print("about                 - About Ultron")
        print("version               - Show current version")
        print("clear                 - Clear the screen")
        print("show memories         - Show all saved memories")
        print("delete memory X       - Delete memory by number")
        print("update memory X TEXT  - Update memory by number")
        print("search KEYWORD        - Search saved memories")
        print("who am i              - Show your saved profile")
        print("history               - Show command history")
        print("show settings         - Show all settings")
        print("set KEY VALUE         - Update setting")
        print("reset settings        - Reset settings")
        print("profile show          - Show user profile")
        print("profile set KEY VALUE - Update profile data")
        print("profile delete KEY    - Delete profile data")
        print("profile reset         - Reset profile")
        print("backup                - Create backup")
        print("backup list           - Show all backups")
        print("backup latest         - Show latest backup")
        print("backup count          - Show total backups")
        print("backup delete NAME    - Delete backup")
        print("backup info NAME      - Show backup details")
        print("restore NAME          - Restore backup")
        print("export memories       - Export memories")
        print("export profile        - Export profile")
        print("export all            - Export all data")
        print("import memories       - Import memories")
        print("import profile        - Import profile")
        print("import all            - Import all data")
        print("show logs             - Show all logs")
        print("clear logs            - Clear all logs")
        print("search logs KEYWORD   - Search logs")
        print("suggest COMMAND       - Suggest matching commands")
        print("exit                  - Close Ultron")
        print("==============================\n")

        return True


    elif user == "about":

        print(f"\n{APP_NAME} AI Assistant")
        print(f"Developer : {DEVELOPER}")
        print("Language  : Python")
        print(f"Status    : {STATUS}\n")

        return True


    elif user == "version":

        print(f"\nCurrent Version : {VERSION}\n")

        return True


    elif user == "clear":

        os.system("cls")

        return True


    elif user == "exit":

        return False


    return False