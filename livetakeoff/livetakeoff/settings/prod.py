import os
import dj_database_url
from .common import *

DEBUG = False

SECRET_KEY = os.environ.get('SECRET_KEY')

ALLOWED_HOSTS = ['api-livetakeoff.herokuapp.com']

DATABASES = {
    # This function looks for an environment variable called DATABASE_URL
    'default': dj_database_url.config()
}