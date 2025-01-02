from dataclasses import dataclass

import pytest

from app.cardmanager import models
from src.adapters.repository import SqlAlchemyUIDMappingRepositoriy
from src.adapters.rfid_interface import (
    AbstractRFIDModule,
    Action,
    BaseDataclassConverter,
    ResponseHandler,
    RFIDData,
    RFIDResponse,
    TagRegister,
    get_action,
)


@dataclass
class ExtendedDataClass(BaseDataclassConverter):
    key: str
    value: int


@pytest.fixture
def extended_data_class():
    return ExtendedDataClass(key="foo", value=42)


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
    def __init__(self):
        self.previous_response = None
        self.current_response = None
        self.event = RFIDData()

    def read(self) -> RFIDData:
        return self.event

    def write(self, text: str):
        pass

    def cleanup(self):
        pass


def test_register_rfid_tags(session):

    # output_file = tmp_path / "output.json"
    rifd_data_samples = [
        RFIDData(uid=10000000),
        RFIDData(uid=10000000),
        RFIDData(),
        RFIDData(uid=10000001),
        RFIDData(uid=10000002),
        RFIDData(uid=10000001),
    ]
    mapping = {
        10000000: "name_0",
        10000001: "name_1",
        10000002: "name_2",
    }
    expected = [
        (10000000, "name_0"),
        (10000001, "name_1"),
        (10000002, "name_2"),
    ]
    registry = SqlAlchemyUIDMappingRepositoriy(session)
    rfid_module = FakeRFIDModule()
    tag_registry = TagRegister(registry, rfid_module, mapping)
    for rifd_data in rifd_data_samples:
        rfid_module.event = rifd_data
        tag_registry.register()
    output = session.query(models.Card.uid, models.Card.name).all()
    assert output == expected


def test_rfid_reader_reads_same_data():
    """The rfid module reads data with a high frequency. Only a change in the received
    data should be recorded"""
    rfid_data_samples = [
        RFIDData(uid=10000000),
        RFIDData(uid=10000000),
        RFIDData(),
        RFIDData(uid=10000001),
        RFIDData(),
        RFIDData(),
        RFIDData(uid=10000002),
    ]
    expected_recording = [
        {"iter": 0, "rfid_data": RFIDData(10000000)},
        {"iter": 2, "rfid_data": RFIDData(None, None)},
        {"iter": 3, "rfid_data": RFIDData(10000001)},
        {"iter": 4, "rfid_data": RFIDData(None, None)},
        {"iter": 6, "rfid_data": RFIDData(10000002)},
    ]
    out = []
    rfid_module = FakeRFIDModule()
    response = RFIDResponse()
    for iter_, rfid_data_sample in enumerate(rfid_data_samples):
        rfid_module.event = rfid_data_sample
        response.current = rfid_module.read()
        response_handler = ResponseHandler(response)
        handled_response = response_handler.handle()
        if handled_response:
            out.append({"iter": iter_, "rfid_data": handled_response})
        response.update()

    assert out == expected_recording


@pytest.mark.parametrize(
    "rfid_data, expected",
    [
        (RFIDData(10000000, ""), Action("play", 10000000)),
        (RFIDData(10000000, "test"), Action("play", 10000000)),
        (RFIDData(None, None), Action("pause")),
    ],
)
def test_rfid_to_action(rfid_data, expected):
    action = get_action(rfid_data)
    assert action == expected


def test_e2e():
    rfid_data_samples = [
        RFIDData(uid=10000000),
        RFIDData(uid=10000000),
        RFIDData(),
        RFIDData(uid=10000001),
        RFIDData(),
        RFIDData(),
        RFIDData(uid=10000002),
    ]
    expexted_queue = [
        '{"action": "play", "uid": 10000000}',
        '{"action": "pause", "uid": null}',
        '{"action": "play", "uid": 10000001}',
        '{"action": "pause", "uid": null}',
        '{"action": "play", "uid": 10000002}',
    ]
    queue_client = FakeQueueClient()
    rfid_module = FakeRFIDModule()
    response = RFIDResponse()
    for rfid_data_sample in rfid_data_samples:
        rfid_module.event = rfid_data_sample
        response.current = rfid_module.read()
        response_handler = ResponseHandler(response)
        handled_response = response_handler.handle()
        if handled_response:
            action = get_action(handled_response)
            message_json = action.to_json()
            queue_client.send_message(message_json)
        response.update()
    assert queue_client.queue == expexted_queue


def test_to_dict_funcionality_for_dataclass(extended_data_class):
    assert {"key": "foo", "value": 42} == extended_data_class.to_dict()


def test_to_json_funcionality_for_dataclass(extended_data_class):
    assert '{"key": "foo", "value": 42}' == extended_data_class.to_json()


# rfid module continuously reading signal
# when no tag is exposed to the reader, the expected response is None, when
# a rfid is hold to the reader, the response the returning of an RFIDData object
