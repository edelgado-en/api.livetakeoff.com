import os
import dj_database_url
from .common import *

DEBUG = False

SECRET_KEY = os.environ.get('SECRET_KEY')

SIMPLE_JWT = {
    'AUTH_HEADER_TYPES': ('JWT',),
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'ACCESS_TOKEN_LIFETIME': datetime.timedelta(days=90),         # 90 days
    'REFRESH_TOKEN_LIFETIME': datetime.timedelta(days=90),        # 90 days
}

ALLOWED_HOSTS = ['api-livetakeoff.herokuapp.com']

DATABASES = {
    # This function looks for an environment variable called DATABASE_URL
    'default': dj_database_url.config()
}

# Tell Django the request is secure if this header is present (needed for Heroku and other proxies)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Force all HTTP traffic to redirect to HTTPS
SECURE_SSL_REDIRECT = True

# Ensure cookies are only sent over HTTPS
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True