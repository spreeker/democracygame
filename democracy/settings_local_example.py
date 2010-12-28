"""This is an example of a local_settings.py module needed by democracy Change as
needed and rename it to local_settings.py """

from settings import * 

DEBUG = True
TEMPLATE_DEBUG = True

#CACHE_BACKEND = 'memcached://127.0.0.1:11211/'
#CACHE_BACKEND = 'dummy:///'

SECRET_KEY = 'SERVER SPECIFIC DO NOT SHARE!'

ADMIN_MEDIA_PREFIX = '/admin_media/'

DATABASES = {
    'default' : {
        'ENGINE':  'django.db.backends.postgresql_psycopg2',
        'NAME' : 'democracy',
#        'NAME' : 'demo',
#        'USER' : 'demo',
#        'PASSWORD' : 'demo',
        'USER' : 'democracy',
        'PASSWORD' : 'democracy',
        'HOST' : 'preeker.net',
    }        
}

TEST_DATABASE_NAME = 'demo_test'

PISTON_DISPLAY_ERRORS = True

INTERNAL_IPS = ('127.0.0.1', 
        '192.168.1.102', 
        '212.123.133.176', 
        '146.50.78.130', 
        '::ffff:127.0.0.1', 
        ) 

EMAIL_HOST = "smtp.online.nl"
DEFAULT_FROM_EMAIL = "stephan@preeker.net"

MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
INSTALLED_APPS += ('debug_toolbar',)

# comment out in production
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}

LOG_FILE_NAME = os.path.join(PROJECT_PATH, "democracy_log.txt")

logging.basicConfig(
    level = logging.DEBUG,
    format = '%(asctime)s %(levelname)s %(message)s',
    filename = LOG_FILE_NAME,
)
