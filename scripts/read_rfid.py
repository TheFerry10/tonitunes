from time import sleep

from mfrc522 import SimpleMFRC522
from RPi import GPIO

reader = SimpleMFRC522()

try:
    while True:
        # print("Hold a tag near the reader")
        response_count = 0
        while response_count < 2:
            id = reader.read_id_no_block()
            if id:
                break
            response_count += 1
        print("ID: %s" % (id))
        sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()
    raise
