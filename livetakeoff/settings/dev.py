from .common import *

DEBUG = True

SECRET_KEY = 'django-insecure-d%uch@2(_k%1#ur9abrpe&=9u_g&@q@y&-eyg54w5a9xv-%^2u'

SIMPLE_JWT = {
    'AUTH_HEADER_TYPES': ('JWT',),
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'ACCESS_TOKEN_LIFETIME': datetime.timedelta(minutes=800),
    'REFRESH_TOKEN_LIFETIME': datetime.timedelta(days=2),
}

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'livetakeoff',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
    }
}