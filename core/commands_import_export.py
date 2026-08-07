from core.import_data import (
    import_memories,
    import_profile,
    import_all
)


def handle_import_export_commands(user):

    if user == "import memories":

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

    return False