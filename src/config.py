import json
import os

from dotenv import load_dotenv
from pydantic import BaseModel, PositiveInt


ROOTDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SETTINGS_FILE_PATH = os.path.join(ROOTDIR, "settings.json")
ENV_FILE_PATH = os.path.join(ROOTDIR, ".env")
ENVIRONMENT = os.environ.get("ENVIRONMENT", "default")

load_dotenv(ENV_FILE_PATH, override=True)


with open(SETTINGS_FILE_PATH, "r", encoding="utf8") as f:
    settings = json.load(f)




class GPIOSettings(BaseModel):
    pin_clk: PositiveInt
    pin_dt: PositiveInt
    button_pin_next: PositiveInt
    button_pin_previous: PositiveInt


class PlayerSettings(BaseModel):
    vlc_instance_params: str = ""
    volume_step: PositiveInt = 5


class Settings(BaseModel):
    gpio_settings: GPIOSettings
    player_settings: PlayerSettings


class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY") or "hard to guess string"
    AUDIO_DIR = os.getenv("AUDIO_DIR")
    FLASK_APP = "cardmanager.py"
    TONITUNES_HOME = os.getenv("TONITUNES_HOME")
    TONITUNES_SONGS_DIR = os.path.join(TONITUNES_HOME, "songs")
    TONITUNES_CARDS_DIR = os.path.join(TONITUNES_HOME, "cards")
    DATABASE_URI = f"sqlite:///{TONITUNES_HOME}/sqlite/data.sqlite"
    gpio_config = GPIOSettings(**settings.get("gpio"))
    player_config = PlayerSettings(**settings.get("player"))


class DevelopmentConfig(Config):
    FLASK_CONFIG = "development"
    DEBUG = True


class TestingConfig(Config):
    FLASK_CONFIG = "testing"
    TESTING = True


class ProductionConfig(Config):
    FLASK_CONFIG = "production"
    DEBUG = False


config = {
    "default": DevelopmentConfig,
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
