import json
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Dict, Literal, Optional

from src.adapters.repository import AbstractUIDMappingRepository


@dataclass
class BaseDataclassConverter:
    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(asdict(self))


@dataclass
class RFIDData(BaseDataclassConverter):
    uid: Optional[int] = None
    text: Optional[str] = None


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


class ResponseHandler:
    def __init__(self, response: RFIDResponse, response_map=None):
        self.response = response
        self.response_map = response_map

    def handle(self) -> RFIDData:
        if not self.response.is_current_eq_previous():
            return self.response.current


@dataclass
class Action(BaseDataclassConverter):
    action: Literal["play", "pause"]
    uid: Optional[str] = None


def get_action(rfid: RFIDData) -> Action:
    if rfid.uid:
        return Action("play", rfid.uid)
    return Action("pause")


class TagRegister:
    def __init__(
        self,
        registry: AbstractUIDMappingRepository,
        rfid_module: AbstractRFIDModule,
        mapping: Optional[Dict[str, str]] = None,
    ):
        self.registry = registry
        self.rfid_module = rfid_module
        self.mapping = mapping

    def get_name_from_mapping(self, rfid_response: RFIDData) -> Optional[str]:
        if self.mapping:
            return self.mapping.get(rfid_response.uid)

    def register(self, name: Optional[str] = None):
        rfid_response = self.rfid_module.read()
        if rfid_response.uid:
            if name is None:
                name = self.get_name_from_mapping(rfid_response)
            self.registry.add(uid=rfid_response.uid, name=name)
            self.registry.save()
