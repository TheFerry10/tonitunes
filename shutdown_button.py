import os
import time

import RPi.GPIO as GPIO

# Use BCM pin numbering
GPIO.setmode(GPIO.BCM)

# Set up GPIO pin 3 as an input with a pull-up resistor
GPIO.setup(3, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def shutdown(channel):
    os.system("sudo shutdown now")


# Add an event listener to detect button press
GPIO.add_event_detect(3, GPIO.FALLING, callback=shutdown, bouncetime=1000)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()
