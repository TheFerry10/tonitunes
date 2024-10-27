import base64
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import pygame
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.storage.queue import QueueServiceClient
from dotenv import load_dotenv
from mapper import FilePathMapper

# https://stackoverflow.com/questions/66866839/pygame-no-mixer-module-found
load_dotenv(override=True)


def process_message(message: dict):
    pass


AUDIO_DIR = os.environ.get("AUDIO_DIR")
MEDIA_MAPPING_PATH = os.environ.get("MEDIA_MAPPING_PATH")
AZURE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
QUEUE_NAME = os.getenv("AZURE_QUEUE_NAME")
queue_service_client = QueueServiceClient.from_connection_string(
    AZURE_CONNECTION_STRING
)

# Create a queue client for the given queue
queue_client = queue_service_client.get_queue_client(queue=QUEUE_NAME)
try:

    # Create the queue if it does not exist
    queue_client.create_queue()
    print(f"Queue '{QUEUE_NAME}' created successfully.")

except ResourceExistsError:
    print(f"Queue '{QUEUE_NAME}' already exists.")
except Exception as e:
    print(f"An error occurred: {e}")

queue_client.clear_messages()

file_path_mapper = FilePathMapper(
    media_mapping_path=MEDIA_MAPPING_PATH, audio_dir=AUDIO_DIR
)

pygame.mixer.init()


def play_playlist(playlist: List[Path]):
    for filepath in playlist:
        play_music(filepath)


# Function to play music from a file
def play_music(filepath):
    if pygame.mixer.get_busy():
        stop_music()

    pygame.mixer.music.load(filepath)
    pygame.mixer.music.play()


# Function to stop music playback
def stop_music():
    pygame.mixer.music.stop()


def pause():
    pygame.mixer.music.pause()


def unpause():
    pygame.mixer.music.unpause()


@dataclass
class AudioAction:
    """
    Actions to control the audio playback: play, stop, pause, unpause
    """

    action: str
    audio_file_path: Optional[Path] = None


def listen_to_queue():
    print(f"Listening to the Azure Storage Queue: {QUEUE_NAME}...")

    while True:
        try:
            messages = queue_client.receive_messages(
                messages_per_page=1, visibility_timeout=30
            )

            for msg in messages:
                # Print the message content
                decoded_message = base64.b64decode(msg.content).decode("utf-8")
                message = json.loads(decoded_message)
                audio_id = str(message.get("id"))
                audio_file_path = file_path_mapper.get_file_path_from_id(audio_id)
                command = AudioAction(
                    **{"action": "play", "audio_file_path": audio_file_path}
                )

                if command.action == "play":
                    play_music(command.audio_file_path)
                    print(f"Playing {command.audio_file_path}")

                elif command.action == "stop":
                    stop_music()
                    print("Music stopped")
                    queue_client.delete_message(msg)

                queue_client.delete_message(msg)
                print(f"Message deleted: {msg.id}")

        except ResourceNotFoundError as e:
            print(f"Error: {e}")
            break  # Stop if the queue does not exist

        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(5)  # Wait a bit before retrying


if __name__ == "__main__":
    try:
        listen_to_queue()
    except KeyboardInterrupt:
        print("Stopping queue listener.")
