import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Optional, Union

from dataclasses_json import dataclass_json

from adapters.repository import AbstractCardRepository, SqlAlchemyCardRepositoriy
from adapters.rfid_interface import RFIDData
from app.cardmanager import models
from player.player import VlcAudioController, create_playlist

logger = logging.getLogger(__name__)


@dataclass_json
@dataclass
class PlayerAction:
    action: Literal["play", "pause"]
    uid: Optional[str] = None


def rfid_to_player_action(rfid_data: RFIDData) -> PlayerAction:
    if rfid_data.uid:
        return PlayerAction("play", rfid_data.uid)
    return PlayerAction("pause")


class RFIDCardManager:
    def __init__(self, registry: AbstractCardRepository):
        self.registry = registry

    def add_card_to_registry(self, rfid_data: RFIDData, card_name: str = None):
        if self.is_card_registered(rfid_data):
            self.handle_existing_card(rfid_data, card_name)
        else:
            self.handle_new_card(rfid_data, card_name)

    def handle_existing_card(self, rfid_data: RFIDData, card_name: str):
        logging.info("Uid %s with name %s already registered", rfid_data.uid, card_name)
        self.registry.update(uid=rfid_data.uid, name=card_name)
        self.registry.save()
        logger.info(
            "Successfully updated uid %s with name %s",
            rfid_data.uid,
            card_name,
        )

    def handle_new_card(self, rfid_data: RFIDData, card_name: str):
        self.registry.add(uid=rfid_data.uid, name=card_name)

    def is_card_registered(self, rfid_data: RFIDData) -> bool:
        return self.registry.get_by_uid(rfid_data.uid) is not None


class AudioControllerCommand(ABC):
    def __init__(self, action: str):
        self.action = action
        self.timestamp = datetime.now()

    @abstractmethod
    def execute(self, audio_controller: VlcAudioController):
        """Execute the command"""


class PlayCommand(AudioControllerCommand):
    def __init__(self, playlist):
        super().__init__("play")
        self.playlist = playlist

    def execute(self, audio_controller: VlcAudioController):
        audio_controller.load_playlist(self.playlist)
        audio_controller.play()


class PauseCommand(AudioControllerCommand):
    def __init__(self):
        super().__init__("pause")

    def execute(self, audio_controller: VlcAudioController):
        audio_controller.pause()


class SkipCommand(AudioControllerCommand):
    def __init__(self):
        super().__init__("skip")

    def execute(self, audio_controller):
        pass


class PlayerActionHandler:
    def __init__(self, repository: SqlAlchemyCardRepositoriy):
        # TODO this is an event handler which will produce a command
        self.repository = repository

    def _handle_play_action(
        self, player_action: PlayerAction
    ) -> Union[PlayCommand, SkipCommand]:
        card: models.Card = self.repository.get_by_uid(player_action.uid)
        if card:
            playlist_as_file_paths = card.get_playlist_as_file_paths()
            if playlist_as_file_paths:
                playlist = create_playlist(playlist_as_file_paths)
                return PlayCommand(playlist=playlist)
        logging.warning(
            f"No playlist defined for card {card}, action uid {player_action.uid}"
        )
        return SkipCommand()

    def _handle_pause_action(self) -> PauseCommand:

        return PauseCommand()

    def handle(self, player_action: PlayerAction) -> AudioControllerCommand:
        if player_action.action == "play":
            return self._handle_play_action(player_action)
        elif player_action.action == "pause":
            return self._handle_pause_action()
        else:
            logging.warning("No handler for action %s", player_action.action)


class CommandQueue:
    def __init__(self):
        # TODO needs to be refined
        self.queue = []

    def add(self, command: AudioControllerCommand):
        self.queue.append(command)

    def execute(self, audio_controller: VlcAudioController):
        for command in self.queue:
            command.execute(audio_controller)
        self.queue = []
