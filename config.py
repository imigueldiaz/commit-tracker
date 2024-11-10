import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Basic Flask config
    SECRET_KEY = 'dev'

    # Database config
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'instance', 'commit_tracker.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload config
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size