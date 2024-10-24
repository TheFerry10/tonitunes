import json
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Literal, Optional


@dataclass
class BaseDataclassConverter:
    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(asdict(self))


@dataclass
class RFIDData(BaseDataclassConverter):
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

    @abstractmethod
    def write(self, text: str):
        """Write text to uid"""

    @abstractmethod
    def cleanup(self):
        """Cleanup reader module"""


class RFIDResponse:
    def __init__(
        self, current: Optional[RFIDData] = None, previous: Optional[RFIDData] = None
    ):
        self.previous = previous
        self.current = current

    def update(self):
        self.previous = self.current

    def is_current_eq_previous(self) -> bool:
        return self.previous == self.current


def handle_response(response: RFIDResponse) -> RFIDData:
    if not response.is_current_eq_previous():
        return response.current


@dataclass
class Action(BaseDataclassConverter):
    action: Literal["play", "pause"]
    uid: Optional[str] = None


def get_action(rfid: RFIDData) -> Action:
    if rfid.uid:
        return Action("play", rfid.uid)
    return Action("pause")
