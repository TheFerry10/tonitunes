from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal, Optional


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


class RFIDResponse:
    def __init__(self, current: RFIDData, previous: RFIDData = None):
        self.previous = previous
        self.current = current

    def update(self):
        self.previous = self.current

    def is_current_eq_previous(self):
        return self.previous == self.current


def handle_response(response: RFIDResponse) -> RFIDData:
    if not response.is_current_eq_previous():
        return response.current


def get_action(rfid: RFIDData):
    if rfid.uid:
        return Action("play", rfid.uid)
    return Action("pause")


@dataclass
class Action:
    action: Literal["play", "pause"]
    uid: Optional[str] = None
