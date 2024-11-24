import json
import logging
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Dict, Literal, Optional


from adapters.repository import AbstractUIDMappingRepository

logger = logging.getLogger(__name__)


@dataclass
class BaseDataclassConverter:
    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(asdict(self))


@dataclass
class RFIDData(BaseDataclassConverter):
    uid: Optional[str] = None
    text: Optional[str] = None

    def __post_init__(self):
        # Convert uid to a string if it's an integer
        if isinstance(self.uid, int):
            self.uid = str(self.uid)


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
        self.response = RFIDResponse()

    def get_name_from_mapping(self, rfid_response: RFIDData) -> Optional[str]:
        if self.mapping:
            return self.mapping.get(rfid_response.uid)

    def register(self, name: Optional[str] = None):
        self.response.current = self.rfid_module.read()
        response_handler = ResponseHandler(self.response)
        handled_response = response_handler.handle()
        if handled_response:
            if self.response.current.uid:
                if name is None:
                    name = self.get_name_from_mapping(self.response.current)
                    print(name)
                    if self.registry.get_by_uid(self.response.current.uid) is None:
                        self.registry.add(uid=self.response.current.uid, name=name)
                        self.registry.save()
                        logger.info(
                            "Successfully registered uid %s with name %s",
                            self.response.current.uid,
                            name,
                        )
                    else:
                        logging.info("UID %s already registered")

        self.response.update()
