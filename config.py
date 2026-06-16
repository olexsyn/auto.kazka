import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DEBUG = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
