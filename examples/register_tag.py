import logging

from RPi import GPIO

from adapters.repository import JsonUIDMappingRepository
from adapters.rfid_interface import TagRegister
from rfid.mfrc import MFRCModule

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

output_file = "out.json"
registry = JsonUIDMappingRepository(output_file)
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
