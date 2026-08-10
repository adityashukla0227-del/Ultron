from core.memory import (
    get_memory,
    save_memory,
    update_memory,
    delete_memory,
    search_memory,
    check_similar_memory,
    cleanup_memories,
    get_memory_stats
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

    elif user == "cleanup memories":

        removed_count = cleanup_memories()

        if removed_count > 0:
            print(
                f"\nUltron: Memory cleanup completed. "
                f"{removed_count} duplicate memories removed.\n"
            )
        else:
            print("\nUltron: No duplicate memories found.\n")

        return True

    elif user == "memory stats":

        stats = get_memory_stats()

        print("\n===== MEMORY INSIGHTS =====")

        print(f"Total Memories: {stats['total']}")
        print(f"Unique Memories: {stats['unique']}")
        print(f"Duplicate Memories: {stats['duplicates']}")
        print(f"Empty Memories: {stats['empty']}")
        print(f"Average Memory Length: {stats['average_length']} characters")

        if stats["longest"]:
            print(f"Longest Memory: {stats['longest']}")
        else:
            print("Longest Memory: None")

        if stats["shortest"]:
            print(f"Shortest Memory: {stats['shortest']}")
        else:
            print("Shortest Memory: None")

        print("===========================\n")

        return True

    elif user.startswith("save memory "):

        memory = user.replace("save memory ", "", 1).strip()

        if not memory:
            print("\nUltron: Memory cannot be empty.\n")
            return True

        similar_memories = check_similar_memory(memory)

        if similar_memories:
            print("\nUltron: This memory already exists:")
            for existing_memory in similar_memories:
                print(f"- {existing_memory}")

            print()
            return True

        save_memory(memory)

        print("\nUltron: Memory saved successfully.\n")

        return True

    elif user.startswith("delete memory "):

        memory = int(user.replace("delete memory ", "", 1).strip())

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

        try:
            old_memory = int(old_memory)
        except ValueError:
            print("\nUltron: Memory number must be a number.\n")
            return True

        new_memory = parts[1].strip()

        if not new_memory:
            print("\nUltron: New memory cannot be empty.\n")
            return True

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