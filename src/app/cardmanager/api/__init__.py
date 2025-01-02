from flask import Blueprint

api = Blueprint("api", __name__, url_prefix="/api")

from . import card, playlist, song  # noqa: F401 E402
