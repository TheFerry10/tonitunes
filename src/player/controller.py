import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import Dict, Literal, Optional, List
from datetime import datetime


from adapters.repository import AbstractCardRepository, SqlAlchemyCardRepositoriy
from adapters.rfid_interface import RFIDData, ResponseHandler, AbstractRFIDModule
from player.player import VlcAudioController, create_playlist
from pathlib import Path
from app.cardmanager import models


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
        audio_controller.play_playlist()


class PauseCommand(AudioControllerCommand):
    def __init__(self):
        super().__init__("pause")

    def execute(self, audio_controller: VlcAudioController):
        audio_controller.pause()


class PlayerActionHandler:
    def __init__(self, repository: SqlAlchemyCardRepositoriy):
        # TODO would be better if repository can be AbstractCardRepository but that
        # would require the manual creation of sql alchemy agnostic models
        self.action_mapping = {
            "play": self.handle_play_action,
            "pause": self.handle_pause_action,
        }
        self.repository = repository

    def handle_play_action(self, player_action: PlayerAction) -> PlayCommand:
        card: models.Card = self.repository.get_by_uid(player_action.uid)
        if card:
            playlist_as_file_paths = card.get_playlist_as_file_paths()
            playlist = create_playlist(playlist_as_file_paths)
            # TODO send this to command queue
            return PlayCommand(playlist=playlist)
        else:
            print("No playlist defined for card")

    def handle_pause_action(self) -> PauseCommand:
        # TODO send this to command queue
        return PauseCommand()

    def handle(self, player_action: PlayerAction) -> AudioControllerCommand:
        if player_action.action == "play":
            return self.handle_play_action(player_action)
        elif player_action.action == "pause":
            return self.handle_pause_action()
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


# class TagRegister:
#     def __init__(
#         self,
#         registry: AbstractUIDMappingRepository,
#         rfid_module: AbstractRFIDModule,
#         mapping: Optional[Dict[str, str]] = None,
#     ):
#         self.registry = registry
#         self.rfid_module = rfid_module
#         self.mapping = mapping
#         self.response = RFIDResponse()

#     def get_name_from_mapping(self, rfid_response: RFIDData) -> Optional[str]:
#         if self.mapping:
#             return self.mapping.get(rfid_response.uid)

#     def register(self, name: Optional[str] = None):
#         self.response.current = self.rfid_module.read()
#         response_handler = ResponseHandler(self.response)
#         handled_response = response_handler.handle()
#         if handled_response:
#             if self.response.current.uid:
#                 if self.registry.get_by_uid(self.response.current.uid) is None:
#                     name = input("Enter card name: ")
#                     self.registry.add(uid=self.response.current.uid, name=name)
#                     self.registry.save()
#                     logger.info(
#                         "Successfully registered uid %s with name %s",
#                         self.response.current.uid,
#                         name,
#                     )
#                 else:
#                     logging.info("UID %s already registered", self.response.current.uid)

#         self.response.update()
