"""This is an example of a local_settings.py module needed by Emocracy Change as
needed and rename it to local_settings.py """


SECRET_KEY = 'SERVER SPECIFIC DO NOT SHARE!'

CONSUMER_KEY = "emocracy consumer key"
CONSUMER_SECRET = "emocracy consumer secret"

DATABASE_ENGINE = 'postgresql_psycopg2'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'thirdparty'

DATABASE_USER = 'thirdparty'             # Not used with sqlite3.
DATABASE_PASSWORD = 'thirdparty'         # Not used with sqlite3.
DATABASE_HOST = 'localhost'             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.
