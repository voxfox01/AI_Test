
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()

def _ensure_database(database_uri: str) -> None:
    """Create the database specified in ``database_uri`` if it does not exist."""
    engine = create_engine(database_uri)
    try:
        engine.connect().close()
    except OperationalError:
        url = engine.url
        default_url = url.set(database="postgres")
        tmp_engine = create_engine(default_url)
        conn = tmp_engine.connect()
        conn.execution_options(isolation_level="AUTOCOMMIT").execute(
            text(f"CREATE DATABASE {url.database}")
        )
        conn.close()
        tmp_engine.dispose()
    finally:
        engine.dispose()


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

    _ensure_database(app.config['SQLALCHEMY_DATABASE_URI'])

    db.init_app(app)
    login_manager.init_app(app)

    from . import routes
    app.register_blueprint(routes.bp)

    with app.app_context():
        db.create_all()

    return app
