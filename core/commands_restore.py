from core.restore import restore_backup


def handle_restore_commands(user):

    if user.startswith("restore "):

        backup_name = user.replace("restore ", "", 1).strip()

        if restore_backup(backup_name):

            print("\nUltron: Backup restored successfully.\n")

        else:

            print("\nUltron: Backup not found.\n")

        return True

    return False