import os
from core.config import APP_NAME, VERSION, DEVELOPER, STATUS


def handle_command(user):
    if user == "help":
        print("\n========== COMMANDS ==========")
        print("help      - Show all commands")
        print("about     - About Ultron")
        print("version   - Show current version")
        print("clear     - Clear the screen")
        print("exit      - Close Ultron")
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

    return False