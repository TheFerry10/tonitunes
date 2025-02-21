from abc import ABC, abstractmethod

from adapters.rfid_interface import AbstractRFIDModule, RFIDData, RFIDReadError


class AbstractMFRC522(ABC):
    @abstractmethod
    def read_no_block(self) -> RFIDData:
        """Read uid and text information"""


class MFRCModule(AbstractRFIDModule):
    MAX_RESPONSE_COUNT = 2

    def __init__(self, reader: AbstractMFRC522):
        self.reader = reader
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
            raise RFIDReadError(f"Failed to read from RFID module: {e}") from e
