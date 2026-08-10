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


def get_relevant_memories(query):
    memories = get_memory()

    if not query:
        return []

    query = query.lower().strip()
    query_words = query.split()

    scored_memories = []
    seen_memories = set()

    for memory in memories:
        memory_lower = memory.lower()

        # Normalize spaces and capitalization
        memory_key = " ".join(memory_lower.split())

        # Skip duplicate memories
        if memory_key in seen_memories:
            continue

        score = 0

        # Exact query match gets highest priority
        if query in memory_lower:
            score += 10

        # Score individual query words
        for word in query_words:
            if word in memory_lower:
                score += 1

        if score > 0:
            scored_memories.append((score, memory))
            seen_memories.add(memory_key)

    # Highest score first
    scored_memories.sort(
        key=lambda item: item[0],
        reverse=True
    )

    return [
        memory
        for score, memory in scored_memories
    ]


def check_similar_memory(text):
    memories = get_memory()

    if not text:
        return []

    text_normalized = " ".join(text.lower().split())

    similar_memories = []

    for memory in memories:
        memory_normalized = " ".join(memory.lower().split())

        # Exact duplicate
        if text_normalized == memory_normalized:
            similar_memories.append(memory)

    return similar_memories

def cleanup_memories():
    memories = get_memory()

    if not memories:
        return 0

    cleaned_memories = []
    seen_memories = set()

    for memory in memories:

        # Normalize spaces and capitalization
        normalized_memory = " ".join(memory.lower().split())

        # Skip empty memories
        if not normalized_memory:
            continue

        # Skip duplicates
        if normalized_memory in seen_memories:
            continue

        seen_memories.add(normalized_memory)
        cleaned_memories.append(memory)

    removed_count = len(memories) - len(cleaned_memories)

    with open(MEMORY_FILE, "w") as file:
        for memory in cleaned_memories:
            file.write(memory + "\n")

    return removed_count

def get_memory_stats():
    memories = get_memory()

    total_memories = len(memories)

    unique_memories = []
    seen_memories = set()

    empty_memories = 0

    for memory in memories:

        normalized_memory = " ".join(memory.lower().split())

        if not normalized_memory:
            empty_memories += 1
            continue

        if normalized_memory not in seen_memories:
            seen_memories.add(normalized_memory)
            unique_memories.append(memory)

    unique_count = len(unique_memories)

    duplicate_count = total_memories - unique_count - empty_memories

    if unique_memories:
        average_length = round(
            sum(len(memory) for memory in unique_memories)
            / unique_count,
            1
        )

        longest_memory = max(
            unique_memories,
            key=len
        )

        shortest_memory = min(
            unique_memories,
            key=len
        )
    else:
        average_length = 0
        longest_memory = ""
        shortest_memory = ""

    return {
        "total": total_memories,
        "unique": unique_count,
        "duplicates": duplicate_count,
        "empty": empty_memories,
        "average_length": average_length,
        "longest": longest_memory,
        "shortest": shortest_memory
    }