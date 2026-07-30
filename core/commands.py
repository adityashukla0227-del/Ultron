import os
from core.config import APP_NAME, VERSION, DEVELOPER, STATUS
from core.memory import get_memory, delete_memory


def handle_command(user):
    if user == "help":
        print("\n========== COMMANDS ==========")
        print("help             - Show all commands")
        print("about            - About Ultron")
        print("version          - Show current version")
        print("clear            - Clear the screen")
        print("show memories    - Show all saved memories")
        print("delete memory X  - Delete memory by number")
        print("exit             - Close Ultron")
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

    elif user == "show memories":
        memories = get_memory()

        if not memories:
            print("\nUltron: No memories found.\n")
        else:
            print("\n===== SAVED MEMORIES =====")
            for index, memory in enumerate(memories, start=1):
                print(f"{index}. {memory}")
            print("==========================\n")

        return True

    elif user.startswith("delete memory "):
        try:
            index = int(user.replace("delete memory ", ""))
            if delete_memory(index):
                print("\nUltron: Memory deleted successfully.\n")
            else:
                print("\nUltron: Invalid memory number.\n")
        except ValueError:
            print("\nUltron: Please enter a valid memory number.\n")

        return True

    elif user == "clear":
        os.system("cls")
        return True

    return False