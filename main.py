from core.config import APP_NAME, VERSION
from core.commands import handle_command
from core.conversation import handle_conversation
from core.memory import save_memory

print("=" * 40)
print(f"🤖 {APP_NAME} {VERSION}")
print("=" * 40)

name = input("Enter your name: ")

print(f"\nHello {name}!")
print("Type 'help' to see available commands.")
print("Type 'exit' anytime to close Ultron.")
print("Type 'remember <text>' to save a memory.\n")

while True:
    user = input(f"{name}: ").strip().lower()

    if user == "exit":
        print(f"\n{APP_NAME}: Goodbye {name}! See you soon.")
        break

    elif user.startswith("remember "):
        text = user.replace("remember ", "", 1)
        save_memory(text)
        print(f"{APP_NAME}: Okay! I'll remember that.")

    elif handle_command(user):
        continue

    elif handle_conversation(user):
        continue

    else:
        print(f"{APP_NAME}: Sorry, I don't understand that yet.")