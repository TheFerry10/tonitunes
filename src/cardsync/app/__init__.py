from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from .database import init_db
from config import config

bootstrap = Bootstrap()
moment = Moment()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    moment.init_app(app)
    init_db()

    from .main import main as main_blueprint

    app.register_blueprint(main_blueprint)
    return app
