"""This is an example of a local_settings.py module needed by Emocracy Change as
needed and rename it to local_settings.py """

SECRET_KEY = 'SERVER SPECIFIC DO NOT SHARE!'
DEBUG = True
CONSUMER_KEY = "abc"
CONSUMER_SECRET = "abc"

REALM = 'emo.preeker.net'

EMOCRACY_API_SERVER = "http://emo.preeker.net/"

DATABASE_ENGINE = 'sqlite3'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'thirdparty.sqlite3'

DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

#EMAIL_HOST = 'smtp.gmail.com'
#EMAIL_PORT = 465 
#EMAIL_HOST_USER = 'spreeker@gmail.com'
#EMAIL_HOST_PASSWORD  = 'ppre7117'
#EMAIL_USE_TLS = True

EMAIL_HOST = 'smtp.telfort.nl'
EMAIL_PORT = 25 
#EMAIL_HOST_USER = 'spreeker@gmail.com'
#EMAIL_HOST_PASSWORD  = 'ppre7117'
#EMAIL_USE_TLS = True
INTERNAL_IPS = ('127.0.0.1' ,'192.168.1.33' , '212.123.133.176', '146.50.78.130', )
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.csrf.middleware.CsrfMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    # for the transaction middleware see :
    # http://docs.djangoproject.com/en/dev/topics/db/transactions/
    'django.middleware.transaction.TransactionMiddleware',
)
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.sites',
    'debug_toolbar',
    'thirdparty.ajax',
    'thirdparty.web',
    'thirdparty.profiles',
    'thirdparty.registration',
    'thirdparty.oauth_consumer',
)

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}
