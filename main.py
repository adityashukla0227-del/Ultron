from core.config import APP_NAME, VERSION
from core.commands import handle_command
from core.conversation import handle_conversation
from core.memory import save_memory
from core.profile import save_profile
from core.history import add_history


print("=" * 40)
print(f"🤖 {APP_NAME} {VERSION}")
print("=" * 40)

name = input("Enter your name: ")

print(f"\nHello {name}!")
print("Type 'help' to see available commands.")
print("Type 'exit' anytime to close Ultron.")
print("Type 'remember <text>' to save a memory.")
print("Type 'my name is <name>' to save your name.")
print("Type 'set <key> <value>' to update settings.\n")


while True:

    raw_user = input(f"{name}: ").strip()

    user = raw_user.lower()

    # Save every command to history
    add_history(user)


    if user == "exit":

        print(f"\n{APP_NAME}: Goodbye {name}! See you soon.")
        break


    elif user.startswith("my name is "):

        name_value = raw_user.replace("my name is ", "", 1).strip()

        save_profile("name", name_value)

        print(
            f"{APP_NAME}: Nice to meet you, {name_value}! I'll remember your name."
        )


    elif user.startswith("remember "):

        text = raw_user.replace("remember ", "", 1).strip()

        save_memory(text)

        print(f"{APP_NAME}: Okay! I'll remember that.")


    elif handle_command(raw_user):

        continue


    elif handle_conversation(user):

        continue


    else:

        print(f"{APP_NAME}: Sorry, I don't understand that yet.")