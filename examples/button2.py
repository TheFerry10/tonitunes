from gpiozero import Button
from signal import pause

BLUE_BUTTON_PIN = 26
RED_BUTTON_PIN = 19

# Initialize buttons with pull-up resistors (default behavior)
blue_button = Button(BLUE_BUTTON_PIN, pull_up=True)
red_button = Button(RED_BUTTON_PIN, pull_up=True)

counter = 0


# Define actions for button press and release
def blue_button_pressed():
    global counter
    counter += 1
    print("The blue button is pressed!")
    print("Counter:", counter)


def blue_button_released():
    print("The blue button is released!")


def red_button_pressed():
    global counter
    counter -= 1
    print("The red button is pressed!")
    print("Counter:", counter)


def red_button_released():
    print("The red button is released!")


# Attach actions to button events
blue_button.when_pressed = blue_button_pressed
blue_button.when_released = blue_button_released
red_button.when_pressed = red_button_pressed
red_button.when_released = red_button_released

# Keep the program running
print("Press the blue or red button...")
pause()
