from gpiozero import RotaryEncoder
from gpiozero import Button
from signal import pause

# Define GPIO pins for clk and dt
clk = 20
dt = 21
sw = 16

# Initialize the rotary encoder
encoder = RotaryEncoder(clk, dt, max_steps=0)  # Set max_steps=0 for unlimited steps
button = Button(sw, pull_up=True)
counter = 0


# Define actions for button press and release
def button_pressed():
    global counter
    counter += 1
    print("The button is pressed!")
    print("Counter:", counter)


def button_released():
    print("The button is released!")


STEP = 5


# Event to trigger when the encoder moves
def on_rotate():
    print("Counter:", encoder.steps)


def on_clockwise_rotate():

    print("Increase volume by ", STEP)


def on_counter_clockwise_rotate():
    print("Decrease volume by ", STEP)


# Attach the event
# encoder.when_rotated = on_rotate
encoder.when_rotated_clockwise = on_clockwise_rotate
encoder.when_rotated_counter_clockwise = on_counter_clockwise_rotate
# Attach actions to button events
button.when_pressed = button_pressed
button.when_released = button_released

# Keep the program running
print("Rotary encoder is ready. Rotate to see the counter...")
pause()
