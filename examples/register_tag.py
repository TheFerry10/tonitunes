import logging

from dotenv import load_dotenv
from RPi import GPIO

from adapters.repository import SqlAlchemyUIDMappingRepositoriy
from adapters.rfid_interface import TagRegister
from app.cardmanager.db import db_session, init_db
from rfid.mfrc import MFRCModule

load_dotenv(override=True)
init_db()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

registry = SqlAlchemyUIDMappingRepositoriy(db_session)
rfid_module = MFRCModule()
mapping = {"79164808694": "sample"}
tag_registry = TagRegister(registry, rfid_module, mapping=mapping)

try:
    while True:
        tag_registry.register()
except KeyboardInterrupt:
    print("KeyboardInterrupt detected. Cleaning up...")
finally:
    GPIO.cleanup()
    print("Cleaning done")
