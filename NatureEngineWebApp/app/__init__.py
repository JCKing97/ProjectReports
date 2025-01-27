"""__init__.py: Sets up the flask app and it's various extensions for the Nature Engine web app"""

__author__ = "James King adapted from Miguel Grinberg Flask Mega Tutorial"

import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from redis import Redis
import rq
from config import Config
import os

# Create the relevant extension objects for Flask as global variables
bootstrap = Bootstrap()
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'login'


def create_app(config_class=Config):
    """
    Create an instance of the flask application with the details of logging, database, redis, migrations and bootstrap
    set up. Set the app up based on the config passed.
    :param config_class: The configuration class that the application should use
    :return: The instance of a flask app
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    app.redis = Redis.from_url(app.config['REDIS_URL'])
    app.task_queue = rq.Queue('nature_engine_tasks', connection=app.redis, default_timeout=300000)

    db.init_app(app)
    migrate.init_app(app, db)
    bootstrap.init_app(app)
    login.init_app(app)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    from app.indir_rec import bp as indir_rec_bp
    app.register_blueprint(indir_rec_bp)

    # Set up the settings for when server is in production
    if not app.debug and not app.testing:

        # Set up logs when in production
        if app.config['LOG_TO_STDOUT']:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            app.logger.addHandler(stream_handler)
        else:
            if not os.path.exists('logs'):
                os.mkdir('logs')
            file_handler = RotatingFileHandler('logs/natureengine.log', maxBytes=10240,
                                               backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Nature Engine startup')

    return app


from app import models

