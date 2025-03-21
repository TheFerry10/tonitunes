import configparser
import logging
import os

from dotenv import load_dotenv
from pydantic import BaseModel, PositiveFloat, PositiveInt

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

ROOTDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SETTINGS_FILE_PATH = os.path.join(ROOTDIR, "settings.ini")
ENV_FILE_PATH = os.path.join(ROOTDIR, ".env")
load_dotenv(ENV_FILE_PATH, override=True)


settings = configparser.ConfigParser()
settings.read(SETTINGS_FILE_PATH)


class GPIOSettings(BaseModel):
    pin_clk: PositiveInt
    pin_dt: PositiveInt
    button_pin_next: PositiveInt
    button_pin_previous: PositiveInt


class PlayerSettings(BaseModel):
    vlc_instance_params: str = ""
    volume_step: PositiveInt = 5


class RfidReaderSettings(BaseModel):
    timeout_between_reads_in_seconds: PositiveFloat = 3.0


class Settings(BaseModel):
    gpio_settings: GPIOSettings
    player_settings: PlayerSettings
    rfid_reader_settings: RfidReaderSettings


class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASK_CONFIG = "development"
    SECRET_KEY = os.environ.get("SECRET_KEY") or "hard to guess string"
    AUDIO_DIR = os.getenv("AUDIO_DIR")
    FLASK_APP = "cardmanager.py"
    TONITUNES_HOME = os.getenv("TONITUNES_HOME")
    TONITUNES_SONGS_DIR = os.path.join(TONITUNES_HOME, "songs")
    TONITUNES_CARDS_DIR = os.path.join(TONITUNES_HOME, "cards")
    DATABASE_URI = f"sqlite:///{TONITUNES_HOME}/sqlite/data.sqlite"
    SETTINGS = settings


class DevelopmentConfig(Config):
    FLASK_CONFIG = "development"
    DEBUG = True


class TestingConfig(Config):
    FLASK_CONFIG = "testing"
    TESTING = True
    TONITUNES_SONGS_DIR = os.path.join(ROOTDIR, "src/app/resources", "songs")
    TONITUNES_CARDS_DIR = os.path.join(ROOTDIR, "src/app/resources", "cards")
    DATABASE_URI = "sqlite:///" + os.path.join(
        ROOTDIR, "src/app/resources/sqlite/test-data.sqlite"
    )


class ProductionConfig(Config):
    FLASK_CONFIG = "production"
    DEBUG = False


config = {
    "default": DevelopmentConfig,
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
