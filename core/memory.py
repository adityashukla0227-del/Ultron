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