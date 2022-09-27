import os
import dj_database_url
from .common import *

DEBUG = False

SECRET_KEY = os.environ.get('SECRET_KEY')

SIMPLE_JWT = {
    'AUTH_HEADER_TYPES': ('JWT',),
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'ACCESS_TOKEN_LIFETIME': datetime.timedelta(minutes=10080),
    'REFRESH_TOKEN_LIFETIME': datetime.timedelta(days=7),
}

ALLOWED_HOSTS = ['api-livetakeoff.herokuapp.com']

DATABASES = {
    # This function looks for an environment variable called DATABASE_URL
    'default': dj_database_url.config()
}