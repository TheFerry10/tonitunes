from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class RFIDData:
    uid: int
    text: str


class RFIDReadError(Exception):
    """Raised when an error occurs while reading from the RFID module."""

    def __init__(self, message="Error reading from RFID module"):
        self.message = message
        super().__init__(self.message)


class RFIDWriteError(Exception):
    """Raised when an error occurs while writing to the RFID module."""

    def __init__(self, message="Error writing to RFID module"):
        self.message = message
        super().__init__(self.message)


class AbstractRFIDModule(ABC):
    @abstractmethod
    def read(self):
        """Read uid and text information"""
        pass

    @abstractmethod
    def write(self, text: str):
        """Write text to uid"""
        pass

    @abstractmethod
    def cleanup(self):
        """Cleanup reader module"""
        pass


def handle_response(rfid_module: AbstractRFIDModule):
    previous_response = None  # init
    current_response = rfid_module.read()
    if previous_response != current_response:
        # None == None
        # 100 == 100
        return current_response
