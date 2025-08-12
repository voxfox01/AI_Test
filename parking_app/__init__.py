
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()


def create_app(config_object=None):
    app = Flask(__name__)

    # Credentials
    db_url = os.environ.get("DATABASE_URL")
    secret_key = os.environ.get("SECRET_KEY", "dev-insecure")

    app.config.from_mapping(
        SECRET_KEY=secret_key,
        SQLALCHEMY_DATABASE_URI=db_url,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    if config_object:
        app.config.from_object(config_object)

    db.init_app(app)
    login_manager.init_app(app)

    from . import routes
    app.register_blueprint(routes.bp)

    with app.app_context():
        db.create_all()

    return app
