from gpiozero import LED

led = LED(16)

while True:
    led.on()
