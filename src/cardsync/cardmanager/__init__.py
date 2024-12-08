import click
from cardmanager import models
from cardmanager.db import bind_query_property, db_session, init_db
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment

from config import config

bootstrap = Bootstrap()
moment = Moment()


def create_app(config_name="default"):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config[config_name])
    bootstrap.init_app(app)
    moment.init_app(app)
    bind_query_property()

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    @app.cli.command("init-db")
    def initialize_database():
        """Initialize the database."""
        init_db()
        click.echo("Database initialized.")

    @app.shell_context_processor
    def make_shell_context():
        return {
            "db_session": db_session,
            "Card": models.Card,
            "Song": models.Song,
            "Playlist": models.Playlist,
        }

    from .main import main as main_blueprint

    app.register_blueprint(main_blueprint)

    from .api import api as api_blueprint

    app.register_blueprint(api_blueprint)

    return app
