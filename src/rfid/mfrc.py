from mfrc522 import SimpleMFRC522
from RPi import GPIO

from adapters.rfid_interface import (
    AbstractRFIDModule,
    RFIDData,
    RFIDReadError,
    RFIDWriteError,
)


class MFRCModule(AbstractRFIDModule):
    MAX_RESPONSE_COUNT = 2

    def __init__(self):
        self.reader = SimpleMFRC522()
        self.event = RFIDData()

    def read(self) -> RFIDData:
        try:
            response_count = 0
            self.event = RFIDData()
            while response_count < self.MAX_RESPONSE_COUNT:
                uid, text = self.reader.read_no_block()
                if uid:
                    self.event = RFIDData(uid, text)
                    return self.event
                response_count += 1
            return self.event
        except Exception as e:
            raise RFIDReadError("Failed to read from RFID module") from e

    def write(self, text: str):
        try:
            self.reader.write(text)
        except Exception as e:
            raise RFIDWriteError("Failed to write to RFID module") from e

    def cleanup(self):
        GPIO.cleanup()
