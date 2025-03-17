import logging
import os
import sys
from time import sleep

from gpiozero import Button

from config import config

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)
config_name = os.getenv("TONITUNES_CONFIG_NAME", "default")
application_config = config.get(config_name)
application_settings = application_config.SETTINGS
gpio_settings = application_settings["gpio"]

shutdown_pin = gpio_settings.getint("button_pin_shutdown")
button_shutdown = Button(shutdown_pin)


def is_root():
    if os.getuid() != 0:
        return False
    else:
        return True


def main():
    logging.info("\nMonitoring pin {} for reboot signal.".format(shutdown_pin))
    logging.info("Ctrl-C to quit.\n")

    try:
        while True:
            if button_shutdown.is_pressed:
                sleep(0.5)
                if button_shutdown.is_pressed:
                    os.system("shutdown now -h")
            sleep(0.1)

    except KeyboardInterrupt:
        logging.info("\n\nKeyboard interrupt.")


if __name__ == "__main__":
    if not (is_root()):
        print("\nScript must be run as root.")
        sys.exit(1)
    else:
        main()
        sys.exit(0)
