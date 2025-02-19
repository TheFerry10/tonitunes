import os
from dotenv import load_dotenv
from dataclasses import dataclass
from dataclasses_json import dataclass_json
import json

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()
with open("settings.json", "r", encoding="utf8") as f:
    settings = json.load(f)

DEFAULT_DATABASE_PATH = os.path.abspath(f"/home/{os.getenv('USER')}/tmp/default.db")
DEFAULT_DATABASE_URI = f"sqlite:///{DEFAULT_DATABASE_PATH}"


@dataclass_json
@dataclass
class GPIOConfig:
    pin_clk: int
    pin_dt: int
    button_pin_next: int
    button_pin_previous: int


@dataclass_json
@dataclass
class PlayerConfig:
    vlc_instance_params: str = ""
    volume_step: int = 5


class Config:
    AUDIO_DIR = os.getenv("AUDIO_DIR")
    FLASK_APP = "cardmanager.py"
    DATABASE_URI = os.getenv("DATABASE_URI", DEFAULT_DATABASE_URI)
    gpio_config = GPIOConfig.from_dict(settings["gpio"])
    player_config = PlayerConfig.from_dict(settings["player"])


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
