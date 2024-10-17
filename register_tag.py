import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from adapters.repository import JsonUIDMappingRepository
from time import sleep

def transform_user_input_to_binary(user_input: str) -> bool:
    user_input = user_input.lower()
    if user_input == "y":
        return True
    elif user_input == "n":
        return False
    else:
        raise ValueError(f"Input {user_input} not valid. Choose 'y' or 'n'.")

file_name = "output.json"
mapping = JsonUIDMappingRepository(file_name)
rfid_read = SimpleMFRC522()

while True:
    # read uid from rfid chip
    print("Hold a tag near the reader")
    try:
        uid, _ = rfid_read.read()
    except KeyboardInterrupt:
        print("KeyboardInterrupt detected. Cleaning up...")
    finally:
        GPIO.cleanup()
        print("Cleaning done")
    
    print(f"UID: {uid}")
    # uid = input("enter uid: ")
    if mapping.get_by_uid(uid):
        print("UID exists...")
        overwrite = transform_user_input_to_binary(input("Overwrite? y/n "))
        if overwrite:
            name = input("Enter name: ")
            mapping.add(uid = uid, name = name, path="/some/random/file.txt")
    else:
        name = input("Enter name: ")
        mapping.add(uid = uid, name = name, path="/some/random/file.txt")
        
    mapping.save()
    
    




