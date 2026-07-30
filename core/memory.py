MEMORY_FILE = "data/memory.txt"

def save_memory(text):
    with open(MEMORY_FILE, "a") as file:
        file.write(text + "\n")