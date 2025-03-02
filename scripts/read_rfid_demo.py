import logging
from time import sleep

from mfrc522 import SimpleMFRC522
from RPi import GPIO
import os
from config import config, Config

config_name = os.getenv("TONITUNES_CONFIG_NAME", "default")
application_config: Config = config.get(config_name)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

reader = SimpleMFRC522()

try:
    while True:
        logging.info("Hold a tag near the reader")
        response_count = 0
        while response_count < 2:
            id = reader.read_id_no_block()
            if id:
                break
            response_count += 1
        logging.info("ID: %s" % (id))
        sleep(
            application_config.SETTINGS.getint(
                "rfid-reader", "timeout_between_reads_in_seconds"
            )
        )
except KeyboardInterrupt:
    GPIO.cleanup()
    raise
