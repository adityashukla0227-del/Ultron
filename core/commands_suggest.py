from core.command_suggestions import suggest_command


def handle_suggest_commands(user):

    if user.startswith("suggest "):

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

    return False