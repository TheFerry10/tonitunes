import json
import os

from dotenv import load_dotenv
from pydantic import BaseModel, PositiveInt

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(override=True)
with open("settings.json", "r", encoding="utf8") as f:
    settings = json.load(f)

DEFAULT_DATABASE_PATH = os.path.abspath(f"/home/{os.getenv('USER')}/tmp/default.db")
DEFAULT_DATABASE_URI = f"sqlite:///{DEFAULT_DATABASE_PATH}"


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
    AUDIO_DIR = os.getenv("AUDIO_DIR")
    FLASK_APP = "cardmanager.py"
    DATABASE_URI = os.getenv("DATABASE_URI", DEFAULT_DATABASE_URI)
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
