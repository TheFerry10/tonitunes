from dataclasses import dataclass
from dataclasses_json import dataclass_json
import pytest
from adapters.repository import SqlAlchemyCardRepositoriy
from adapters.rfid_interface import RFIDData
from player.controller import RFIDCardManager


@pytest.fixture
def test_class():
    @dataclass_json
    @dataclass
    class TestClass:
        key: str
        value: int

    return TestClass(key="foo", value=42)


def test_add_card_to_registry_when_not_exist(session):
    registry = SqlAlchemyCardRepositoriy(session)
    card_manager = RFIDCardManager(registry)
    rfid_data = RFIDData(uid=10000000, text="test")
    card_manager.add_card_to_registry(rfid_data, "name_0")
    assert registry.get_by_uid(10000000).name == "name_0"


def test_update_card_name_when_exists(session):
    registry = SqlAlchemyCardRepositoriy(session)
    card_manager = RFIDCardManager(registry)
    rfid_data = RFIDData(uid=10000000, text="test")
    card_manager.add_card_to_registry(rfid_data, "name_0")
    card_manager.add_card_to_registry(rfid_data, "name_1")
    assert registry.get_by_uid(10000000).name == "name_1"


def test_to_dict_funcionality_for_dataclass(test_class):

    assert {"key": "foo", "value": 42} == test_class.to_dict()


def test_to_json_funcionality_for_dataclass(test_class):

    assert '{"key": "foo", "value": 42}' == test_class.to_json()
