import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from config import config, Config
from adapters.repository import CsvCardRepository, UIDAlreadyExistsError
import os

ENVIRONMENT = os.environ.get("TONITUNES_ENV", "default")
application_config: Config = config.get(ENVIRONMENT)

def transform_user_input_to_binary(user_input: str) -> bool:
    user_input = user_input.lower()
    if user_input == "y":
        return True
    elif user_input == "n":
        return False
    else:
        raise ValueError(f"Input {user_input} not valid. Choose 'y' or 'n'.")


def start_registration():
    file_name = os.path.join(application_config.TONITUNES_CARDS_DIR, "cards.csv")
    mapping = CsvCardRepository(file_name)
    rfid_read = SimpleMFRC522()
    try:
        while True:
            print("Hold a tag near the reader")
            uid, _ = rfid_read.read()
            print(f"UID: {uid}")
            if mapping.get_by_uid(uid):
                print("UID exists...")
                overwrite = transform_user_input_to_binary(input("Overwrite? y/n "))
                if overwrite:
                    name = input("Enter name: ")
                    try:
                        mapping.add(uid=uid, name=name)
                    except UIDAlreadyExistsError:
                        print(f"UID {uid} already exists")
                        break 
            else:
                name = input("Enter name: ")
                mapping.add(uid=uid, name=name)

            mapping.save()
    except KeyboardInterrupt:
        print("KeyboardInterrupt detected. Cleaning up...")
    finally:
        GPIO.cleanup()
        print("Cleaning done")



if __name__ == "__main__":
    start_registration()