
from core.config_validator import (
    validate_config,
    config_summary
)

def handle_config_commands(user):

    if user == "config check":

        checks = validate_config()

        print("\n===== CONFIG VALIDATOR =====")

        for key, value in checks.items():

            status = "OK" if value else "FAILED"

            print(f"{key} : {status}")

        print("============================\n")

        return True


    elif user == "config summary":

        summary = config_summary()

        print("\n===== CONFIG SUMMARY =====")

        for key, value in summary.items():

            print(f"{key} : {value}")

        print("==========================\n")

        return True


    return False