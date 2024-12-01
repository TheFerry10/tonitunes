import os


from app import create_app
from app.database import db_session
from app.models import Card, AudioFile, Playlist

app = create_app(os.getenv("FLASK_CONFIG") or "default")


@app.shell_context_processor
def make_shell_context():
    return {
        "db": db_session,
        "Card": Card,
        "AudioFile": AudioFile,
        "Playlist": Playlist,
        "app": app,
    }


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()
