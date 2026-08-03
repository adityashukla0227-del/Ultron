import os

from core.config import APP_NAME, VERSION, DEVELOPER, STATUS

from core.memory import (
    get_memory,
    delete_memory,
    update_memory,
    search_memory
)

from core.profile import get_all_profiles
from core.history import get_history

from core.backup import (
    create_backup,
    list_backups,
    latest_backup,
    backup_count,
    delete_backup,
    backup_info
)

from core.restore import restore_backup

from core.export import (
    export_memories,
    export_profile,
    export_all
)

from core.import_data import (
    import_memories,
    import_profile,
    import_all
)

from core.settings import (
    show_settings,
    update_setting,
    reset_settings
)

from core.profile_manager import (
    show_profile,
    set_profile,
    delete_profile,
    reset_profile
)

from core.logger import (
    get_logs,
    clear_logs,
    search_logs
)

from core.system_health import (
    system_health,
    system_summary
)

from core.config_validator import (
    validate_config,
    config_summary
)

# NEW IMPORT (v0.24)
from core.command_suggestions import suggest_command


def handle_command(user):

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
        print("system health         - Check system health")
        print("system summary        - Show system summary")
        print("config check          - Validate configuration")
        print("config summary        - Show configuration details")
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


    elif user == "who am i":

        profile = get_all_profiles()

        if not profile:
            print("\nUltron: No profile information found.\n")

        else:
            print("\n===== USER PROFILE =====")

            for key, value in profile.items():
                print(f"{key.capitalize()} : {value}")

            print("========================\n")

        return True


    elif user == "history":

        history = get_history()

        if not history:
            print("\nUltron: No command history found.\n")

        else:
            print("\n===== COMMAND HISTORY =====")

            for index, command in enumerate(history, start=1):
                print(f"{index}. {command}")

            print("===========================\n")

        return True

    elif user == "show settings":

        settings = show_settings()

        print("\n===== SETTINGS =====")

        for key, value in settings.items():
            print(f"{key} : {value}")

        print("====================\n")

        return True


    elif user.startswith("set "):

        parts = user.split(" ", 2)

        if len(parts) < 3:
            print("\nUltron: Usage -> set KEY VALUE\n")
            return True

        key = parts[1]
        value = parts[2]

        update_setting(key, value)

        print("\nUltron: Setting updated successfully.\n")

        return True


    elif user == "reset settings":

        reset_settings()

        print("\nUltron: Settings reset successfully.\n")

        return True


    elif user == "profile show":

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


    elif user == "backup":

        if create_backup():

            print("\nUltron: Backup created successfully.\n")

        else:

            print("\nUltron: Backup failed.\n")

        return True


    elif user == "backup list":

        backups = list_backups()

        if not backups:

            print("\nUltron: No backups found.\n")

        else:

            print("\n===== AVAILABLE BACKUPS =====")

            for index, backup in enumerate(backups, start=1):

                print(f"{index}. {backup}")

            print("=============================\n")

        return True

    elif user == "backup latest":

        backup = latest_backup()

        if backup:

            print(f"\nLatest Backup: {backup}\n")

        else:

            print("\nUltron: No backups found.\n")

        return True


    elif user == "backup count":

        print(f"\nTotal Backups: {backup_count()}\n")

        return True


    elif user.startswith("backup delete "):

        name = user.replace("backup delete ", "", 1).strip()

        if delete_backup(name):

            print("\nUltron: Backup deleted successfully.\n")

        else:

            print("\nUltron: Backup not found.\n")

        return True


    elif user.startswith("backup info "):

        name = user.replace("backup info ", "", 1).strip()

        files = backup_info(name)

        if files is None:

            print("\nUltron: Backup not found.\n")

        else:

            print(f"\nBackup Name: {name}")
            print("Files:")

            for file in files:

                print(f"- {file}")

            print()

        return True


    elif user.startswith("restore "):

        backup_name = user.replace("restore ", "", 1).strip()

        if restore_backup(backup_name):

            print("\nUltron: Backup restored successfully.\n")

        else:

            print("\nUltron: Backup not found.\n")

        return True


    elif user == "export memories":

        if export_memories():

            print("\nUltron: Memories exported successfully.\n")

        else:

            print("\nUltron: Export failed.\n")

        return True


    elif user == "export profile":

        if export_profile():

            print("\nUltron: Profile exported successfully.\n")

        else:

            print("\nUltron: Export failed.\n")

        return True


    elif user == "export all":

        if export_all():

            print("\nUltron: All data exported successfully.\n")

        else:

            print("\nUltron: Export failed.\n")

        return True

    elif user == "import memories":

        if import_memories():

            print("\nUltron: Memories imported successfully.\n")

        else:

            print("\nUltron: Import failed.\n")

        return True


    elif user == "import profile":

        if import_profile():

            print("\nUltron: Profile imported successfully.\n")

        else:

            print("\nUltron: Import failed.\n")

        return True


    elif user == "import all":

        if import_all():

            print("\nUltron: All data imported successfully.\n")

        else:

            print("\nUltron: Import failed.\n")

        return True


    elif user == "show logs":

        logs = get_logs()

        if not logs:

            print("\nUltron: No logs found.\n")

        else:

            print("\n========== LOGS ==========")

            for log in logs:

                print(log.strip())

            print("==========================\n")

        return True


    elif user == "clear logs":

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


    elif user == "system health":

        health = system_health()

        print("\n===== SYSTEM HEALTH =====")

        for key, value in health.items():

            print(f"{key.capitalize()} : {value}")

        print("=========================\n")

        return True


    elif user == "system summary":

        summary = system_summary()

        print("\n===== SYSTEM SUMMARY =====")

        for key, value in summary.items():

            print(f"{key.capitalize()} : {value}")

        print("==========================\n")

        return True

    elif user == "config check":

        checks = validate_config()

        print("\n===== CONFIG VALIDATOR =====")

        for key, value in checks.items():

            status = "OK" if value else "FAILED"

            print(f"{key} : {status}")

        print("============================\n")

        return True


    elif user == "config summary":

        summary = config_summary()

        print("\n===== CONFIG SUMMARY =====")

        for key, value in summary.items():

            print(f"{key} : {value}")

        print("==========================\n")

        return True

    elif user.startswith("suggest "):

        keyword = user.replace("suggest ", "", 1).strip()

        suggestions = suggest_command(keyword)

        if not suggestions:

            print("\nUltron: No matching commands found.\n")

        else:

            print("\n===== MATCHING COMMANDS =====")

            for command in suggestions:

                print(command)

            print("=============================\n")

        return True

    elif user == "exit":

        return False

    else:

        print("\nUltron: Unknown command.\n")
        print("Type:")
        print("help")
        print("or")
        print("suggest <keyword>\n")

        return True

    COMMANDS = [
    "help",
    "about",
    "version",
    "clear",

    "show memories",
    "delete memory",
    "update memory",
    "search",

    "who am i",
    "history",

    "show settings",
    "set",
    "reset settings",

    "profile show",
    "profile set",
    "profile delete",
    "profile reset",

    "backup",
    "backup list",
    "backup latest",
    "backup count",
    "backup delete",
    "backup info",

    "restore",

    "export memories",
    "export profile",
    "export all",

    "import memories",
    "import profile",
    "import all",

    "show logs",
    "clear logs",
    "search logs",

    "system health",
    "system summary",

    "config check",
    "config summary",

    "suggest",

    "exit"
]