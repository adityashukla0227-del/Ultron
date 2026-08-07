from core.export import (
    export_memories,
    export_profile,
    export_all
)


def handle_export_commands(user):

    if user == "export memories":

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

    return False