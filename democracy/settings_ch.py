# Django settings for democratiespel project.
from settings import *

import os.path
import os
import sys

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.split(PROJECT_PATH)[0] + '/external_apps/' )

BASE_PATH = os.path.dirname(__file__)

DEBUG = False

SERVER_EMAIL = 'reinder@rustema.nl'
DEFAULT_FROM_EMAIL = 'webmaster@democratiespel.nl'

ADMINS = (
    ('ReindeR Rustema', 'webmaster@democratiespel.nl'),
    ('Stephan Preeker', 'stephan@preeker.net'),
)
DEFAULT_FROM = 'webmaster@democratiespel.nl'

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
# although not all choices may be avilable on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Amsterdam'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
#LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'nl'
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
SECRET_KEY = '5xpy!!naf)+1e6=&amp;%6oa2!u(@0hja#qoo=8)*(!b^x8i3kmgba'


MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'voting.middleware.VoteHistory',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    BASE_PATH+'/templates/',
)

# Override the server-derived value of SCRIPT_NAME 
# See http://code.djangoproject.com/wiki/BackwardsIncompatibleChanges#lighttpdfastcgiandothers
FORCE_SCRIPT_NAME = ''

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.sessions',
    'django.contrib.markup',

    'gamelogic',
    'profiles',
    'api',
    'voting',
    'issue',

    'dashboard',

    'tagging',
    'registration',
    'piston',
    'rosetta',
)

FORCELOWERCASE_TAGS = True
ACCOUNT_ACTIVATION_DAYS = 1

# Set the context processors used by RequestContext objects: 
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'profiles.context_processors.userprofile',
)
# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

FORCELOWERCASE_TAGS = True
MAX_TAG_LENGTH = 30

USE_I18N = True

