from player.controller import rfid_to_player_action, PlayerAction
from adapters.rfid_interface import RFIDData
import pytest


@pytest.mark.parametrize(
    "rfid_data, expected_action",
    [
        (RFIDData("10000000", "test"), PlayerAction("play", "10000000")),
        (RFIDData(), PlayerAction("pause")),
    ],
)
def test_rfid_to_play_action(rfid_data, expected_action):
    action = rfid_to_player_action(rfid_data)
    assert action == expected_action
