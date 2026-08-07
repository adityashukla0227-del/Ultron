from core.backup import (
    create_backup,
    list_backups,
    latest_backup,
    backup_count,
    delete_backup,
    backup_info
)


def handle_backup_commands(user):

    if user == "backup":

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


    return False