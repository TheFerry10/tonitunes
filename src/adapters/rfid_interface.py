import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import Optional


logger = logging.getLogger(__name__)


@dataclass_json
@dataclass
class RFIDData:
    uid: Optional[int] = None
    text: Optional[str] = None


class RFIDReadError(Exception):
    """Raised when an error occurs while reading from the RFID module."""

    def __init__(self, message="Error reading from RFID module"):
        self.message = message
        super().__init__(self.message)


class AbstractRFIDModule(ABC):
    @abstractmethod
    def read(self):
        """Read uid and text information"""


class ResponseHandler:
    """
    A class to handle and compare RFID responses.

    Attributes:
        previous_response (RFIDData): The previous RFID response.
        current_response (RFIDData): The current RFID response.
    """

    def __init__(self, response: RFIDData):
        """
        Initializes the ResponseHandler with an initial RFID response.

        Args:
            response (RFIDData): The initial RFID response.
        """
        self.previous_response = response
        self.current_response = response

    def _is_current_eq_previous(self) -> bool:
        """
        Checks if the current RFID response is equal to the previous response.

        Returns:
            bool: True if the current response is equal to the previous response, False
            otherwise.
        """
        return self.current_response == self.previous_response

    def handle(self, response: RFIDData) -> Optional[RFIDData]:
        """
        Handles a new RFID response. Updates the current response and compares it with
        the previous response.

        Args:
            response (RFIDData): The new RFID response.

        Returns:
            Optional[RFIDData]: The new RFID response if it is different from the
            previous response, None otherwise.
        """
        self.current_response = response
        if not self._is_current_eq_previous():
            self.previous_response = self.current_response
            return self.current_response
        else:
            return None
