from mfrc522 import SimpleMFRC522
from RPi import GPIO

from src.adapters.rfid_interface import (
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
            response_count = 0
            while response_count < 2:
                uid, text = self.reader.read_no_block()
                if uid:
                    break
                response_count += 1
            return RFIDData(uid, text)
        except Exception as e:
            raise RFIDReadError("Failed to read from RFID module") from e

    def write(self, text: str):
        try:
            self.reader.write(text)
        except Exception as e:
            raise RFIDWriteError("Failed to write to RFID module") from e

    def cleanup(self):
        GPIO.cleanup()
