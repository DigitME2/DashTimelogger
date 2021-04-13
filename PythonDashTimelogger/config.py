import os
from os import environ, path

from dotenv import load_dotenv

BASE_DIR = path.abspath(path.dirname(__file__))
load_dotenv(path.join(BASE_DIR, ".env"))

class Config(object):
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or "EdOhMW901yTkiQHbEdOhMW901yTkiQHb"
    FLASK_ENV = 'development'

    DATABASE_USER = 'server'
    DATABASE_ADDRESS = '192.168.174.129'
    DATABASE_PORT = '3306'
    DATABASE_NAME = 'work_tracking'
    DATABASE_PASSWORD = 'gnlPdNTW1HhDuQGc'

    # SQLAlchemy Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'mysql://' + DATABASE_USER + ':' + DATABASE_PASSWORD + '@' + DATABASE_ADDRESS + ':' + DATABASE_PORT + '/' + DATABASE_NAME

    # flask_user
    USER_ENABLE_EMAIL = False
    USER_ENABLE_USERNAME = True
    USER_REQUIRE_RETYPE_PASSWORD = False
    USER_APP_NAME = 'Timelogger visualisation'
    USER_APP_VERSION = '1.0'
    USER_CORPORATION_NAME = 'UCLAN'
    USER_COPYRIGHT_YEAR = '2021'