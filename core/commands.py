import os

from core.config import APP_NAME, VERSION, DEVELOPER, STATUS

from core.commands_system import handle_system_commands

from core.commands_history import handle_history_commands

from core.commands_profile import handle_profile_commands

from core.commands_settings import handle_settings_commands

from core.commands_backup import handle_backup_commands

from core.commands_logs import handle_logs_commands

from core.commands_import_export import handle_import_export_commands

from core.commands_health import handle_health_commands

from core.commands_profile_manager import handle_profile_manager_commands

from core.commands_export import handle_export_commands

from core.commands_config import handle_config_commands

from core.commands_system_summary import handle_system_summary_commands

from core.commands_log_tools import handle_log_tools_commands

from core.commands_restore import handle_restore_commands

from core.commands_suggest import handle_suggest_commands

from core.command_suggestions import suggest_command

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

def handle_command(user):

    if handle_system_commands(user):
        return True

    elif handle_history_commands(user):
        return True

    elif handle_profile_commands(user):
        return True
    
    elif handle_settings_commands(user):
        return True

    elif handle_backup_commands(user):
        return True 

    elif handle_logs_commands(user):
        return True

    elif handle_import_export_commands(user):
        return True

    elif handle_health_commands(user):
        return True

    elif handle_profile_manager_commands(user):
        return True

    elif handle_export_commands(user):
        return True

    elif handle_config_commands(user):
        return True

    elif handle_system_summary_commands(user):
        return True

    elif handle_log_tools_commands(user):
        return True

    elif handle_restore_commands(user):
        return True

    elif handle_suggest_commands(user):
        return True

    else:
        
        suggestion = suggest_command(user)

        print("\nUltron: Unknown command.\n")

        if suggestion:
            print("Did you mean:")
            print(suggestion)
            print()

        print("Type:")
        print("help")
        print("or")
        print("suggest <Keyword>\n")

        return True