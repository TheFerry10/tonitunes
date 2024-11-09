from gpiozero import Button
import RPi.GPIO as GPIO
import time

BLUE_BUTTON_PIN = 26
RED_BUTTON_PIN = 19

# blue_button = Button(BLUE_BUTTON_PIN)
# red_button = Button(RED_BUTTON_PIN)

GPIO.setmode(GPIO.BCM)
GPIO.setup(RED_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BLUE_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Set the GPIO mode to BCM
GPIO.setmode(GPIO.BCM)

# Initialize the pushbutton pin as an input with a pull-up resistor
# The pull-up input pin will be HIGH when the switch is open and LOW when the switch is closed.
# Variable to keep track of the previous button state
prev_button_state_blue = GPIO.input(BLUE_BUTTON_PIN)
prev_button_state_red = GPIO.input(RED_BUTTON_PIN)
counter = 0

try:
    while True:
        # Read the state of the switch/button
        button_state_blue = GPIO.input(BLUE_BUTTON_PIN)
        button_state_red = GPIO.input(RED_BUTTON_PIN)

        # Check if the button state has changed (press or release event)
        if button_state_blue != prev_button_state_blue:
            if button_state_blue == GPIO.LOW:  # Button is pressed
                print("The blue button is pressed!")
                counter += 1
                print(counter)
            else:  # Button is released
                print("The blue button is released!")

            # Update the previous button state
            prev_button_state_blue = button_state_blue

        # Check if the button state has changed (press or release event)
        if button_state_red != prev_button_state_red:
            if button_state_red == GPIO.LOW:  # Button is pressed
                print("The red button is pressed!")
                counter -= 1
                print(counter)
            else:  # Button is released
                print("The red button is released!")

            # Update the previous button state
            prev_button_state_red = button_state_red

        # Small delay to avoid unnecessary reading
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nExiting...")
    # Clean up GPIO settings
    GPIO.cleanup()
