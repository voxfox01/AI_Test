from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


db = SQLAlchemy()
login_manager = LoginManager()


def create_app(config_object=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY='changeme',
        SQLALCHEMY_DATABASE_URI='postgresql+psycopg2://user:password@localhost/parking',
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
