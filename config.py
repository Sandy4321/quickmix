import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SPOTIFY_CLIENT_ID = os.environ['SPOTIFY_CLIENT_ID']
    SPOTIFY_CLIENT_SECRET = os.environ['SPOTIFY_CLIENT_SECRET']

    ## Basic Auth
    BASIC_AUTH_USERNAME = os.environ['BASIC_AUTH_USERNAME']
    BASIC_AUTH_PASSWORD = os.environ['BASIC_AUTH_PASSWORD']

class ProductionConfig(Config):
    DEBUG = False
    REDIRECT_URI = 'http://www.quickmix.io/callback'


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    REDIRECT_URI = 'https://myrunningsongs-stage.herokuapp.com/callback'
    BASIC_AUTH_FORCE = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    REDIRECT_URI = 'http://localhost:5000/callback'


class TestingConfig(Config):
    TESTING = True
