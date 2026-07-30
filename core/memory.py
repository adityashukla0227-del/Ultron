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