COMMAND_ALIASES = {
    # Backup
    "create a backup": "backup",
    "make a backup": "backup",
    "take a backup": "backup",
    "create backup": "backup",
    "make backup": "backup",
    "save a backup": "backup",

    "list my backups": "backup list",
    "show my backups": "backup list",
    "list all my backups": "backup list",
    "what backups do i have": "backup list",

    "show latest backup": "backup latest",
    "show my latest backup": "backup latest",
    "what is my latest backup": "backup latest",

    "how many backups": "backup count",
    "show backup count": "backup count",
    "how many backups do i have": "backup count",

    # Profile
    "show my profile": "profile show",
    "display my profile": "profile show",
    "what is my profile": "profile show",
    "tell me about my profile": "profile show",
    "show my personal information": "profile show",
    "show my personal info": "profile show",

    "reset my profile": "profile reset",

    # History
    "show my history": "history",
    "show history": "history",
    "show my command history": "history",
    "show previous commands": "history",
    "show what i did": "history",

    # Memories
    "show my memories": "show memories",
    "show memories": "show memories",
    "what do you remember": "show memories",
    "what do you remember about me": "show memories",
    "show what you remember": "show memories",
    "tell me what you remember": "show memories",

    "did you remember anything": "show memories",
    "do you remember anything": "show memories",
    "do you remember my memories": "show memories",
    "can you show what you remember": "show memories",

    # Settings
    "show my settings": "show settings",
    "display my settings": "show settings",
    "what are my settings": "show settings",
    "show my current settings": "show settings",

    "reset my settings": "reset settings",

    # Export
    "export my memories": "export memories",
    "export memories": "export memories",
    "save my memories": "export memories",
    "download my memories": "export memories",

    "export my profile": "export profile",
    "export profile": "export profile",
    "save my profile": "export profile",
    "download my profile": "export profile",

    "export all my data": "export all",
    "export all data": "export all",
    "export everything": "export all",
    "save all my data": "export all",

    # Import
    "import my memories": "import memories",
    "import memories": "import memories",
    "restore my memories": "import memories",
    "load my memories": "import memories",

    "import my profile": "import profile",
    "import profile": "import profile",
    "restore my profile": "import profile",
    "load my profile": "import profile",

    "import all my data": "import all",
    "import all data": "import all",
    "restore all my data": "import all",
    "restore everything": "import all",

    # Logs
    "show my logs": "show logs",
    "show logs": "show logs",
    "view my logs": "show logs",
    "display my logs": "show logs",
    "what are my logs": "show logs",

    "clear my logs": "clear logs",
    "clear logs": "clear logs",
    "delete my logs": "clear logs",
    "remove my logs": "clear logs",
    "wipe my logs": "clear logs",

    # System / Help
    "what can you do": "help",
    "what commands do you have": "help",
    "show me available commands": "help",

    "tell me about yourself": "about",
    "who are you": "about",
    "what are you": "about",

    "what version are you": "version",
    "which version are you running": "version",
    "show me your version": "version",

    "clear my screen": "clear",
    "clear the screen": "clear",
    "clean the screen": "clear",

    "quit": "exit",
    "close ultron": "exit",
    "shut down": "exit",
    "goodbye": "exit",

    # System Health
    "check system health": "system health",
    "show system health": "system health",
    "check my system health": "system health",
    "how is the system": "system health",
    "is the system healthy": "system health",
    "is ultron healthy": "system health",
    "check ultron health": "system health",
    "show me system health": "system health",

    # System Summary
    "show system summary": "system summary",
    "show my system summary": "system summary",
    "display system summary": "system summary",
    "display my system summary": "system summary",
    "what is the system summary": "system summary",
    "give me system summary": "system summary",
    "show me system summary": "system summary",
    "tell me about the system": "system summary",

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

def parse_command(user):
    user = user.strip().lower()

    # Memory Search
    prefix = "search my memories for "

    if user.startswith(prefix):
        keyword = user[len(prefix):].strip()

        if keyword:
            return f"search {keyword}"

    # Memory Delete
    prefix = "delete my memory "

    if user.startswith(prefix):
        number = user[len(prefix):].strip()

        if number:
            return f"delete memory {number}"

    # Memory Update
    prefix = "update my memory "

    if user.startswith(prefix) and " to " in user:
        remaining = user[len(prefix):].strip()

        number, new_memory = remaining.split(" to ", 1)

        number = number.strip()
        new_memory = new_memory.strip()

        if number and new_memory:
            return f"update memory {number} {new_memory}"

    # Memory Add
    prefix = "remember that "

    if user.startswith(prefix):
        memory = user[len(prefix):].strip()

        if memory:
            return f"save memory {memory}"

    # Memory List
    if user == "list my memories":
        return "show memories"

    # Memory Context Query
    prefix = "do you remember "

    if user.startswith(prefix):
        query = user[len(prefix):].strip()

        if query:
            return f"do you remember {query}"

    # Backup Info
    prefix = "show info of backup "

    if user.startswith(prefix):
        name = user[len(prefix):].strip()

        if name:
            return f"backup info {name}"

    # Backup Delete
    prefix = "delete backup "

    if user.startswith(prefix):
        name = user[len(prefix):].strip()

        if name:
            return f"backup delete {name}"

    # Profile Set
    prefix = "set my "

    if user.startswith(prefix) and " to " in user:
        remaining = user[len(prefix):].strip()

        key, value = remaining.split(" to ", 1)

        key = key.strip()
        value = value.strip()

        if key and value:
            return f"profile set {key} {value}"

    # Profile Delete
    prefix = "delete my "

    if user.startswith(prefix):
        key = user[len(prefix):].strip()

        if key:
            return f"profile delete {key}"

    prefix = "remove my "

    if user.startswith(prefix):
        key = user[len(prefix):].strip()

        if key:
            return f"profile delete {key}"

    # Profile Change
    prefix = "change my "

    if user.startswith(prefix) and " to " in user:
        remaining = user[len(prefix):].strip()

        key, value = remaining.split(" to ", 1)

        key = key.strip()
        value = value.strip()

        if key and value:
            return f"profile set {key} {value}"

    return None