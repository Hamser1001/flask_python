# import required Flask modules
from flask import Flask

# import database and models from models.py
from models import db

# module for working with file paths
import os

# module for background tasks, celery
from celery import Celery, Task


# create Flask application
app = Flask(__name__)


def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app


# config redis
app.config.from_mapping(
    CELERY=dict(
        broker_url="redis://localhost",
        result_backend="redis://localhost",
        task_ignore_result=True,
    ),
)

celery_app = celery_init_app(app)

# get the absolute path of the current project directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


# ---------------------------
# Application Configuration
# ---------------------------

# configure the SQLite database location
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"sqlite:///{os.path.join(BASE_DIR, 'books.db')}"
)

# disable modification tracking (saves memory and removes warning)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# initialize SQLAlchemy with the Flask app
db.init_app(app)


# ---------------------------
# Create Database Tables
# ---------------------------

# create database tables automatically if they do not exist
with app.app_context():
    db.create_all()


# ---------------------------
# Run the Application
# ---------------------------

from web import *
from tasks import send_book_notification

if __name__ == "__main__":
    # start the Flask development server
    app.run(debug=True)
