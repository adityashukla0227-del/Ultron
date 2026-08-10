from core.memory import get_memory, get_relevant_memories
from core.profile import get_profile


def handle_conversation(user):
    if user == "hi":
        print("Ultron: Hello!")
        return True

    elif user == "how are you":
        print("Ultron: I am working perfectly!")
        return True

    elif user == "what is my name" or user == "who am i":
        name = get_profile("name")

        if name:
            print(f"Ultron: Your name is {name}.")
        else:
            print("Ultron: I don't know your name yet.")
        return True

    elif user.startswith("do you remember"):
        query = user.replace("do you remember", "", 1).strip()

        if query:
            memories = get_relevant_memories(query)

            if memories:
                print("Ultron: Yes, I remember:")
                for memory in memories:
                    print(f"- {memory}")
            else:
                print("Ultron: I don't remember anything about that.")

        else:
            memories = get_memory()

            if memories:
                print("Ultron: I remember these things:")
                for memory in memories:
                    print(f"- {memory}")
            else:
                print("Ultron: I don't remember anything yet.")

        return True

    return False