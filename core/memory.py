MEMORY_FILE = "data/memory.txt"


def save_memory(text):
    with open(MEMORY_FILE, "a") as file:
        file.write(text + "\n")


def get_memory():
    try:
        with open(MEMORY_FILE, "r") as file:
            memories = file.readlines()
            return [memory.strip() for memory in memories]
    except FileNotFoundError:
        return []


def delete_memory(index):
    memories = get_memory()

    if index < 1 or index > len(memories):
        return False

    del memories[index - 1]

    with open(MEMORY_FILE, "w") as file:
        for memory in memories:
            file.write(memory + "\n")

    return True


def update_memory(index, new_text):
    memories = get_memory()

    if index < 1 or index > len(memories):
        return False

    memories[index - 1] = new_text

    with open(MEMORY_FILE, "w") as file:
        for memory in memories:
            file.write(memory + "\n")

    return True


def search_memory(keyword):
    memories = get_memory()

    results = []

    for memory in memories:
        if keyword.lower() in memory.lower():
            results.append(memory)

    return results