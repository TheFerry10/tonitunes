from signal import pause

import vlc
from gpiozero import RotaryEncoder

from player.player import VlcAudioController

file_path = "song.mp3"
vlc_instance = vlc.Instance("--aout=alsa")
VOLUME_STEP = 5
# Define GPIO pins for clk and dt

clk = 20
dt = 21

encoder = RotaryEncoder(clk, dt, max_steps=0)
audio_controller = VlcAudioController(vlc_instance)


def on_clockwise_rotate():
    audio_controller.increase_volume(VOLUME_STEP)
    print("Current volume ", audio_controller.player.audio_get_volume())


def on_counter_clockwise_rotate():
    audio_controller.decrease_volume(VOLUME_STEP)
    print("Current volume ", audio_controller.player.audio_get_volume())


audio_controller.play(file_path)
encoder.when_rotated_clockwise = on_clockwise_rotate
encoder.when_rotated_counter_clockwise = on_counter_clockwise_rotate

# Keep the program running
print("Rotary encoder is ready. Rotate to see the counter...")
pause()
