from core.memory import (
    get_memory,
    update_memory,
    delete_memory,
    search_memory
)


def handle_memory_commands(user):

    if user == "show memories":

        memories = get_memory()

        print("\n===== MEMORIES =====")

        if not memories:
            print("No memories found.")
        else:
            for memory in memories:
                print(memory)

        print("====================\n")

        return True

    elif user.startswith("delete memory "):

        memory = user.replace("delete memory ", "", 1).strip()

        if delete_memory(memory):
            print("\nUltron: Memory deleted successfully.\n")
        else:
            print("\nUltron: Memory not found.\n")

        return True

    elif user.startswith("update memory "):

        parts = user.replace("update memory ", "", 1).split(" ", 1)

        if len(parts) < 2:
            print("\nUltron: Usage -> update memory OLD NEW\n")
            return True

        old_memory = parts[0]
        new_memory = parts[1]

        if update_memory(old_memory, new_memory):
            print("\nUltron: Memory updated successfully.\n")
        else:
            print("\nUltron: Memory not found.\n")

        return True

    elif user.startswith("search "):

        keyword = user.replace("search ", "", 1).strip()

        memories = search_memory(keyword)

        print("\n===== SEARCH RESULTS =====")

        if not memories:
            print("No matching memories found.")
        else:
            for memory in memories:
                print(memory)

        print("==========================\n")

        return True

    return False