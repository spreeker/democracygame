# Django settings for emocracy project.

# This version is specific to an Emocracy install, as things stand this file is 
# tailored to Thijs' computer. 
# Current setup is that of an development server, that is: media server by 
# Django, HTTP request handled by Django, site running on top of SQLite.
# For media stuff look at the base urls.py.

import logging
import os
import sys

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.split(PROJECT_PATH)[0] + '/external_apps/' ) 

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Stephan Preeker', 'stephan@preeker.net'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
#DATABASE_NAME = 'database.sqlite3'             # Or path to database file if using sqlite3.
DATABASE_NAME = os.path.join(PROJECT_PATH, "database.sqlite3")

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
#LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'nl'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

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

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'SHOULD BE IN A SEPARATE SERVER SPECIFIC SETTINGS FILE'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
#    'django.contrib.csrf.middleware.CsrfMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'emocracy.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_PATH, 'templates')
)

AUTH_PROFILE_MODULE = 'accounts.userprofile'

# Set the context processors used by RequestContext objects: 
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'emocracy.web.context_processors.profile',
)

LOGIN_REDIRECT_URL = '/web/issue/'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.webdesign', # for lorem ipsum generator :)
    'django.contrib.sessions',
    'emocracy.gamelogic',
    'emocracy.accounts',
    'emocracy.api',
    'emocracy.web',
	'registration'
)

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# loggin setup:
# (see: http://simonwillison.net/2008/May/22/debugging/ )
# and python docs

LOG_FILE_NAME = os.path.join(PROJECT_PATH, "emocracy_log.txt")

logging.basicConfig(
    level = logging.INFO,
    format = '%(asctime)s %(levelname)s %(message)s',
    filename = LOG_FILE_NAME,
)

ACCOUNT_ACTIVATION_DAYS = 1

try :
	from settings_local import *
except exception:
	print "create your local settings_local.py settings file with password sensitive information ect"
