# Django settings for thirdparty project.

import logging
import os
import sys

SECRET_KEY = 'SERVER SPECIFIC DO NOT SHARE!'
DEBUG = True
CONSUMER_KEY = "abc"
CONSUMER_SECRET = "abc"

REALM = 'd.preeker.net'

DEMOCRACY_API_SERVER = "http://d.preeker.net/"

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.split(PROJECT_PATH)[0] + '/external_apps/' )

BASE_PATH = os.path.dirname(__file__)

DEBUG = True # in production this should be FALSE
TEMPLATE_DEBUG = DEBUG # comment this out in production

SERVER_EMAIL = 'webmaster@democratiespel.nl'

ADMINS = (
    ('Conrado Buhrer', 'conrado@buhrer.net'),
    ('ReindeR Rustema', 'webmaster@democratiespel.nl'),
)

DEFAULT_FROM = 'webmaster@democratiespel.nl'

MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = os.path.join(PROJECT_PATH, "thirdparty.sqlite3")

DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Amsterdam'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = BASE_PATH+'/media'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'iwkgrl8-xd&)jig$_#7du+uj3lrx-*ki-yizt59yqv10&ojnij'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.doc.XViewMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware', # comment this out in production
)

ROOT_URLCONF = 'thirdparty.urls'

# Override the server-derived value of SCRIPT_NAME 
# See http://code.djangoproject.com/wiki/BackwardsIncompatibleChanges#lighttpdfastcgiandothers
FORCE_SCRIPT_NAME = ''

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    BASE_PATH+'/templates/',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.sites',
    'thirdparty.ajax',
    'thirdparty.web',
    'thirdparty.profiles',
    'thirdparty.oauth_consumer',
    'registration',
    #'debug_toolbar', # comment this out in production
)

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# loggin setup:
# (see: http://simonwillison.net/2008/May/22/debugging/ )
# and python docs

#LOG_FILE_NAME = os.path.join(PROJECT_PATH, "thirdparty_log.txt")

#logging.basicConfig(
#    level = logging.INFO,
#    format = '%(asctime)s %(levelname)s %(message)s',
#    filename = LOG_FILE_NAME,
#)

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_URL = '/logout/'

ACCOUNT_ACTIVATION_DAYS = 1
AUTH_PROFILE_MODULE = 'profiles.UserProfile'

