print("=" * 40)
print("🤖 Ultron v0.2")
print("=" * 40)

name = input("Enter your name: ")

print(f"\nHello {name}!")
print("Type 'exit' anytime to close Ultron.\n")

while True:
    user = input(f"{name}: ")

    if user.lower() == "exit":
        print(f"\nGoodbye {name}! See you soon.")
        break

    elif user.lower() == "hi":
        print("Ultron: Hello!")

    elif user.lower() == "how are you":
        print("Ultron: I am working perfectly!")

    else:
        print("Ultron: Sorry, I don't understand that yet.")