COMMAND_ALIASES = {
    # Backup
    "create a backup": "backup",
    "make a backup": "backup",
    "take a backup": "backup",

    "list my backups": "backup list",
    "show my backups": "backup list",

    "show latest backup": "backup latest",
    "show my latest backup": "backup latest",

    "how many backups": "backup count",
    "show backup count": "backup count",

    # Profile
    "show my profile": "profile show",
    "display my profile": "profile show",

    "reset my profile": "profile reset",

    # History
    "show my history": "history",
    "show history": "history",

    # Memories
    "show my memories": "show memories",
    "show memories": "show memories",

    # Settings
    "show my settings": "show settings",
    "display my settings": "show settings",

    "reset my settings": "reset settings",

    # Export
    "export my memories": "export memories",
    "export my profile": "export profile",
    "export all my data": "export all",

    # Import
    "import my memories": "import memories",
    "import my profile": "import profile",
    "import all my data": "import all",

    # Logs
    "show my logs": "show logs",
    "clear my logs": "clear logs",

    # System Health
    "check system health": "system health",
    "show system health": "system health",

    # System Summary
    "show system summary": "system summary",

    # Config
    "check config": "config check",
    "check my config": "config check",
    "show config": "config summary",
    "show my config": "config summary",

    # Profile / Identity
    "what is my name": "who am i",
    "who am i": "who am i",
}


def translate_command(user):
    user = user.strip().lower()

    return COMMAND_ALIASES.get(user)