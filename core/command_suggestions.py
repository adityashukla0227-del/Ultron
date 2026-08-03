from difflib import get_close_matches

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

def suggest_command(keyword):
  """
  Returns closest matching commands.
  """

  keyword = keyword.strip().lower()

  if not keyword:
     return []

  matches = []

  for command in COMMANDS:
    if keyword in command.lower():
       matches.append(command)

  if matches:
     return matches

  close = get_close_matches(
    keyword,
    COMMANDS,
    n=3,
    cutoff=0.5
  )

  return close