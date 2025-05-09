# config.py

# Secret key for encoding JWT tokens and sessions
SECRET_KEY = 'your_secret_key_here'

# Add any other configurations you need, like email or database settings

import os

basedir = os.path.abspath(os.path.dirname(__file__))
SECRET_KEY = os.environ.get("SECRET_KEY", "dev_key")

SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
    "sqlite:///" + os.path.join(basedir, "instance", "db.sqlite3")

SQLALCHEMY_TRACK_MODIFICATIONS = False
