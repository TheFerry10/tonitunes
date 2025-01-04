# Bibliotheken laden
from time import sleep

from gpiozero import LED, PWMLED

LED_PIN = 17

# Initialisierung von GPIO17 als PWM-Signal für LED (Ausgang)
led = PWMLED(LED_PIN)

# Wiederholung einleiten
v = 0
step = 0.01
led.value = 0
for i in range(100):
    v += step
    led.value = v
    sleep(1)
