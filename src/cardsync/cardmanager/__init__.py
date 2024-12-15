"""
This module initializes the Flask application and sets up the database, CLI commands,
and shell context.
"""

import click
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment

from config import config

from . import db, models

bootstrap = Bootstrap()
moment = Moment()


def create_app(config_name="default"):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config[config_name])
    bootstrap.init_app(app)
    moment.init_app(app)
    db.bind_query_property()

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        """Remove the database session at the end of the request."""
        db.db_session.remove()

    @app.cli.command("init-db")
    def initialize_database():
        """Initialize the database."""
        db.init_db()
        click.echo("Database initialized.")

    @app.shell_context_processor
    def make_shell_context():
        """Provide shell context objects for the Flask shell."""
        return {
            "db_session": db.db_session,
            "Card": models.Card,
            "Song": models.Song,
            "Playlist": models.Playlist,
        }

    from .main import main as main_blueprint

    app.register_blueprint(main_blueprint)

    from .api import api as api_blueprint

    app.register_blueprint(api_blueprint)

    return app
