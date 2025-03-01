import logging
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from config import config, Config
from adapters.repository import (
    CsvCardRepository,
    UIDAlreadyExistsError,
    SqlAlchemyCardRepositoriy,
)
import os
from app.cardmanager.db import db_session, init_db
from config import DevelopmentConfig, config

from utils import transform_user_input_to_binary


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

config_name = os.getenv("TONITUNES_CONFIG_NAME", "default")
application_config: Config = config.get(config_name)


def start_registration():
    init_db(application_config.DATABASE_URI)
    session = db_session()
    mapping = SqlAlchemyCardRepositoriy(session)
    rfid_read = SimpleMFRC522()
    try:
        while True:
            logging.info("Hold a tag near the reader")
            uid, _ = rfid_read.read()
            logging.info(f"UID: {uid}")
            if mapping.get_by_uid(uid):
                logging.info("UID exists...")
                overwrite = transform_user_input_to_binary(input("Overwrite? y/n "))
                if overwrite:
                    name = input("Enter name: ")
                    try:
                        mapping.update(uid=uid, name=name)
                    except UIDAlreadyExistsError:
                        logging.info(f"UID {uid} already exists")
                        break
            else:
                name = input("Enter name: ")
                mapping.add(uid=uid, name=name)

            mapping.save()
    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt detected. Cleaning up...")
    finally:
        GPIO.cleanup()
        logging.info("Cleaning done")


if __name__ == "__main__":
    start_registration()
