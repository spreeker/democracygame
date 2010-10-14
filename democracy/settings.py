# Django settings for democracy project.
import logging
import os
import sys

# Be sure to create a settings_local.py module with your local settings!

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
FORCE_SCRIPT_NAME = "" # removes the django.fcgi from the urls.

# Add the external dependencies of democracy to the python path. (The external
# dependencies are included with the democracy source to ease deployment.)
sys.path.append(os.path.split(PROJECT_PATH)[0] + '/external_apps/' ) 
sys.path.append(os.path.split(PROJECT_PATH)[0] + '/external_libraries/' ) 

DEBUG = True  #on production server this should be FASLE
TEMPLATE_DEBUG = True # on production this should be disabeled

ADMINS = (
    ('Stephan Preeker', 'stephan@preeker.net'),
)
MANAGERS = ADMINS

DATABASES = {
    'default' : {
        'ENGINE' : 'django.db.backends.postgresql_psycopg2',
        'NAME' : 'democracy_democratiespel',
        'USER' : 'democracy',
        'PASSWORD' : 'ADkdg5.Q',
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Amsterdam'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'
#LANGUAGE_CODE = 'nl'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

ugettext = lambda s: s
LANGUAGES = (
    ('nl' , ugettext('Dutch')),
    ('en' , ugettext('English')),
    ('es' , ugettext('Spanish')),
    ('de' , ugettext('German')),
    ('fr' , ugettext('French')),
)

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin/media/'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
#    'django.contrib.csrf.middleware.CsrfMiddleware',
    'voting.middleware.VoteHistory',
    'django.middleware.doc.XViewMiddleware',
)
CACHE_MIDDLEWARE_SECONDS = 60
CACHE_MIDDLEWARE_KEY_PREFIX = "demo"

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_PATH, 'templates')
)

# authorization / profile settings:
AUTH_PROFILE_MODULE = 'profiles.userprofile'
LOGIN_URL = '/profile/login/'
LOGIN_REDIRECT_URL = '/'


# Set the context processors used by RequestContext objects: 
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'profiles.context_processors.userprofile',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.sessions',
    'django.contrib.markup',

    'debug_toolbar', # comment out in production!!
    'south', 
    #Democracy
    'gamelogic',
    'profiles',
    'api',
    'voting',
    'issue',
    'juni2010',
    'dashboard',

    # external apps 
    'tagging',
	'registration',
    'piston',
    'rosetta',
)
FORCE_SCRIPT_NAME = "" # removes the django.fcgi from the urls.


# comment out in production
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}

#SESSION_EXPIRE_AT_BROWSER_CLOSE = True
FORCELOWERCASE_TAGS = True

#LOG_FILE_NAME = os.path.join(PROJECT_PATH, "democracy_log.txt")
MAX_TAG_LENGTH = 30

#logging.basicConfig(
#    level = logging.DEBUG,
#    format = '%(asctime)s %(levelname)s %(message)s',
#    filename = LOG_FILE_NAME,
#)

ACCOUNT_ACTIVATION_DAYS = 1
