import pytest
import json
from itertools import cycle
from typing import List

from src.adapters.repository import JsonUIDMappingRepository
from src.adapters.rfid_interface import (
    AbstractRFIDModule,
    RFIDData,
    handle_response,
    RFIDResponse,
    get_action,
    Action,
)


class FakeQueueClient:
    def __init__(self):
        self.queue = []

    def send_message(self, message):
        """Simulate sending a message to the queue."""
        self.queue.append(message)
        return True

    def receive_message(self):
        """Simulate receiving a message from the queue."""
        if self.queue:
            return self.queue.pop(0)
        return None

    def get_queue_length(self):
        """Returns the number of messages in the queue."""
        return len(self.queue)

    def clear_messages(self):
        self.queue = []


class FakeRFIDModule(AbstractRFIDModule):
    def __init__(self, uid_text_samples: List[tuple]):
        self._uid_text_cycle = cycle(uid_text_samples)
        self.previous_response = None
        self.current_response = None

    def read(self) -> RFIDData:
        uid, text = next(self._uid_text_cycle)
        return RFIDData(uid, text)

    def write(self, text: str):
        pass

    def cleanup(self):
        pass


def test_register_rfid_tags(tmp_path):
    output_file = tmp_path / "output.json"
    uid_text_samples = [
        ("10000000", ""),
        ("10000000", ""),
        ("10000001", ""),
        ("10000002", ""),
        ("10000001", ""),
    ]
    uid_name_mapping = {
        "10000000": "name_0",
        "10000001": "name_1",
        "10000002": "name_2",
    }
    expected = {
        "10000000": {"name": "name_0", "path": ""},
        "10000001": {"name": "name_1", "path": ""},
        "10000002": {"name": "name_2", "path": ""},
    }
    mapping = JsonUIDMappingRepository(output_file)
    rfid_module = FakeRFIDModule(uid_text_samples)
    for _ in range(len(uid_text_samples)):
        rfid_response = rfid_module.read()
        name = uid_name_mapping.get(rfid_response.uid)
        mapping.add(uid=rfid_response.uid, name=name, path="")
        mapping.save()
        with open(output_file, encoding="utf8") as f:
            output = json.load(f)
    assert output == expected


def test_rfid_reader_reads_continuously():
    pass


def test_rfid_reader_reads_same_data():
    """The rfid module reads data with a high frequency. Only a change in the received
    data should be recorded"""
    uid_text_samples = [
        ("10000000", ""),
        ("10000000", ""),
        (None, None),
        ("10000001", ""),
        (None, None),
        (None, None),
        ("10000002", ""),
    ]
    RFIDData("10000000", "")
    expected_recording = [
        {"iter": 0, "rfid_data": RFIDData("10000000", "")},
        {"iter": 2, "rfid_data": RFIDData(None, None)},
        {"iter": 3, "rfid_data": RFIDData("10000001", "")},
        {"iter": 4, "rfid_data": RFIDData(None, None)},
        {"iter": 6, "rfid_data": RFIDData("10000002", "")},
    ]
    out = []
    rfid_module = FakeRFIDModule(uid_text_samples)
    response = RFIDResponse(current=None, previous=None)
    for iter_ in range(len(uid_text_samples)):
        response.current = rfid_module.read()
        handled_response = handle_response(response)
        if handled_response:
            out.append({"iter": iter_, "rfid_data": handled_response})
        response.update()

    assert out == expected_recording


@pytest.mark.parametrize(
    "rfid_data, expected",
    [
        (RFIDData("10000000", ""), Action("play", "10000000")),
        (RFIDData("10000000", "test"), Action("play", "10000000")),
        (RFIDData(None, None), Action("pause")),
    ],
)
def test_rfid_to_action(rfid_data, expected):
    action = get_action(rfid_data)
    assert action == expected
