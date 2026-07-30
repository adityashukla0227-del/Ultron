from core.memory import get_memory


def handle_conversation(user):
    if user == "hi":
        print("Ultron: Hello!")
        return True

    elif user == "how are you":
        print("Ultron: I am working perfectly!")
        return True

    elif user.startswith("do you remember"):
        memories = get_memory()

        if memories:
            for memory in memories:
                if memory in user:
                    print(f"Ultron: Yes, I remember {memory}.")
                    return True

            print("Ultron: I remember these things:")
            for memory in memories:
                print(f"- {memory}")
            return True

        else:
            print("Ultron: I don't remember anything yet.")
            return True

    return False