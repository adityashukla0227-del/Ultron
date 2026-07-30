import os

print("=" * 40)
print("🤖 Ultron v0.3")
print("=" * 40)

name = input("Enter your name: ")

print(f"\nHello {name}!")
print("Type 'help' to see available commands.")
print("Type 'exit' anytime to close Ultron.\n")

while True:
    user = input(f"{name}: ").strip().lower()

    if user == "exit":
        print(f"\nUltron: Goodbye {name}! See you soon.")
        break

    elif user == "hi":
        print("Ultron: Hello!")

    elif user == "how are you":
        print("Ultron: I am working perfectly!")

    elif user == "help":
        print("\n========== COMMANDS ==========")
        print("help      - Show all commands")
        print("about     - About Ultron")
        print("version   - Show current version")
        print("clear     - Clear the screen")
        print("exit      - Close Ultron")
        print("==============================\n")

    elif user == "about":
        print("\nUltron AI Assistant")
        print("Developer : Aditya")
        print("Language  : Python")
        print("Status    : Under Development\n")

    elif user == "version":
        print("\nCurrent Version : Ultron v0.3\n")

    elif user == "clear":
        os.system("cls")

    else:
        print("Ultron: Sorry, I don't understand that yet.")