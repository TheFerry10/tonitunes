from mfrc522 import SimpleMFRC522
from RPi import GPIO

from adapters.rfid_interface import (
    AbstractRFIDModule,
    RFIDData,
    RFIDReadError,
    RFIDWriteError,
)


class MFRCModule(AbstractRFIDModule):
    def __init__(self):
        self.reader = SimpleMFRC522()

    def read(self) -> RFIDData:
        try:
            uid, text = self.reader.read_no_block()
            return {"uid": uid, "text": text}
        except Exception as e:
            raise RFIDReadError("Failed to read from RFID module") from e

    def write(self, text: str):
        try:
            self.reader.write(text)
        except Exception as e:
            raise RFIDWriteError("Failed to write to RFID module") from e

    def cleanup(self):
        GPIO.cleanup()
