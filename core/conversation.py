def handle_conversation(user):
    if user == "hi":
        print("Ultron: Hello!")
        return True

    elif user == "how are you":
        print("Ultron: I am working perfectly!")
        return True

    return False