import pytest
import json
from itertools import cycle
from typing import List

from src.adapters.repository import JsonUIDMappingRepository
from src.adapters.rfid_interface import AbstractRFIDModule, RFIDData, handle_response


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
        "10000000": {"name": "name_0", "path": "/some/random/file.txt"},
        "10000001": {"name": "name_1", "path": "/some/random/file.txt"},
        "10000002": {"name": "name_2", "path": "/some/random/file.txt"},
    }
    mapping = JsonUIDMappingRepository(output_file)
    rfid_module = FakeRFIDModule(uid_text_samples)
    for _ in range(len(uid_text_samples)):
        rfid_response = rfid_module.read()
        uid = rfid_response.get("uid")
        name = uid_name_mapping.get(uid)
        mapping.add(uid=uid, name=name, path="/some/random/file.txt")
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
    expected_recording = [
        {"iter": 0, "uid": "10000000"},
        {"iter": 2, "uid": None},
        {"iter": 3, "uid": "10000001"},
        {"iter": 4, "uid": None},
        {"iter": 6, "uid": "10000002"},
    ]
    out = []
    rfid_module = FakeRFIDModule(uid_text_samples)
    previous_response = None  # init
    for iter_ in range(len(uid_text_samples)):
        current_response = rfid_module.read()
        if previous_response != current_response:
            if current_response is None:
                uid = None
            else:
                uid = current_response.uid
            result = {"iter": iter_, "uid": uid}
            out.append(result)
        previous_response = current_response

    assert out == expected_recording
