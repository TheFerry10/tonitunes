from itertools import cycle
from typing import Iterable

from adapters.rfid_interface import ResponseHandler, RFIDData, RFIDReadError
from player.controller import PlayerAction, rfid_to_player_action
from rfid.mfrc import AbstractMFRC522, MFRCModule


class NoMoreSamples(Exception):
    """No more samples to read"""


class FakeMFRC522(AbstractMFRC522):
    def __init__(self, samples: Iterable):
        self._count = 0
        self._samples = samples

    def read_no_block(self):
        try:
            return next(self._samples)
        except StopIteration:
            raise NoMoreSamples("No more samples to read")

    def write(self, text: str):
        pass


def test_mfrc_read():
    expected_rfid_data = RFIDData(uid="12345678", text="sample text")
    samples = cycle(
        [
            (None, None),
            ("12345678", "sample text"),
            ("12345678", "sample text"),
            ("12345678", "sample text"),
            ("12345678", "sample text"),
        ]
    )
    reader = FakeMFRC522(samples)
    rfid_module = MFRCModule(reader)
    assert rfid_module.read() == expected_rfid_data


def test_return_empty_rfid_object_when_previous_is_not_empty():
    initial_response = RFIDData(uid="12345678", text="sample text")
    new_response = RFIDData()
    handler = ResponseHandler(initial_response)
    assert handler.handle(new_response) == new_response


def test_that_current_and_previous_response_is_initially_true():
    initial_response = RFIDData()
    handler = ResponseHandler(initial_response)
    assert handler._is_current_eq_previous()


def test_that_when_initial_response_and_current_response_are_none_return_none():
    initial_response = RFIDData()
    new_response = RFIDData()
    handler = ResponseHandler(initial_response)
    assert handler.handle(new_response) is None


def test_return_response_when_not_equal_to_previous_response():
    initial_response = RFIDData()
    handler = ResponseHandler(initial_response)
    new_response = RFIDData(uid="12345678", text="sample text")
    assert handler.handle(new_response) == new_response


def test_return_none_when_response_equal_to_previous_response():
    initial_response = RFIDData(uid="12345678", text="sample text")
    handler = ResponseHandler(initial_response)
    new_response = RFIDData(uid="12345678", text="sample text")
    assert handler.handle(new_response) is None


def test_response_handler_in_sequence():
    expected_unique_responses = [
        RFIDData("12345678", "sample text"),
        RFIDData("87654321", "sample text 2"),
        RFIDData(None, None),
        RFIDData("12345678", "sample text"),
    ]

    responses = [
        RFIDData(None, None),
        RFIDData(None, None),
        RFIDData("12345678", "sample text"),
        RFIDData("12345678", "sample text"),
        RFIDData("87654321", "sample text 2"),
        RFIDData(None, None),
        RFIDData("12345678", "sample text"),
    ]
    initial_response = RFIDData()
    handler = ResponseHandler(initial_response)
    unique_responses = []
    for response in responses:
        handled_response = handler.handle(response)
        if handled_response:
            unique_responses.append(handled_response)
    assert unique_responses == expected_unique_responses


def test_player_action_handler_in_sequence():
    expected_actions = [
        PlayerAction("play", "12345678"),
        PlayerAction("play", "87654321"),
        PlayerAction("pause"),
        PlayerAction("play", "12345678"),
    ]

    responses = [
        RFIDData(None, None),
        RFIDData(None, None),
        RFIDData("12345678", "sample text"),
        RFIDData("12345678", "sample text"),
        RFIDData("87654321", "sample text 2"),
        RFIDData(None, None),
        RFIDData("12345678", "sample text"),
    ]
    initial_response = RFIDData()
    handler = ResponseHandler(initial_response)
    actions = []
    for response in responses:
        handled_response = handler.handle(response)
        if handled_response:
            action = rfid_to_player_action(handled_response)
            actions.append(action)
    assert actions == expected_actions


def test_mfrc_scenario():
    """The rfid module reads data with a high frequency. Only a change in the received
    data should be recorded"""
    read_sequence = [
        ("12345678", "sample text"),
        ("12345678", "sample text"),
        ("87654321", "sample text 2"),
        (None, None),
        (None, None),
        (None, None),
        (None, None),
        (None, None),
        (None, None),
        ("12345678", "sample text"),
    ]
    expected_states = [
        RFIDData("12345678", "sample text"),
        RFIDData("87654321", "sample text 2"),
        RFIDData(None, None),
        RFIDData("12345678", "sample text"),
    ]

    initial_state = RFIDData()
    handler = ResponseHandler(initial_state)
    reader = FakeMFRC522(iter(read_sequence))
    rfid_module = MFRCModule(reader)
    unique_responses = []

    while True:
        try:
            response = rfid_module.read()
        except RFIDReadError as e:
            assert (
                "Failed to read from RFID module: No more samples to read" == e.message
            )
            break
        handled_response = handler.handle(response)
        if handled_response:
            unique_responses.append(handled_response)
    assert unique_responses == expected_states
