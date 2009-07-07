# Django settings for ededemocracy project.
import logging
import os
import sys

# Be sure to create a settings_local.py module with your local settings!

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
# Add the external dependencies of Edemocracy to the python path. (The external
# dependencies are included with the Edemocracy source to ease deployment.)
sys.path.append(os.path.split(PROJECT_PATH)[0] + '/external_apps/' ) 
sys.path.append(os.path.split(PROJECT_PATH)[0] + '/external_libraries/' ) 

DEBUG = True    #on production server this should be FASLE
TEMPLATE_DEBUG = DEBUG # on production this should be disabeled

ADMINS = (
    # ('Stephan Preeker', 'stephan@preeker.net'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'database.sqlite3'

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
#LANGUAGE_CODE = 'nl'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

ugettext = lambda s: s
LANGUAGES = (
    ('en' , ugettext('English')),
    ('es' , ugettext('Spanish')),
    ('de' , ugettext('German')),
    ('nl' , ugettext('Dutch')),
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
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
#    'django.contrib.csrf.middleware.CsrfMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware', ## !! comment out in production.
)

ROOT_URLCONF = 'edemocracy.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_PATH, 'templates')
)

# authorization / profile settings:
AUTH_PROFILE_MODULE = 'profiles.userprofile'
LOGIN_URL = '/profile/login/'
LOGIN_REDIRECT_URL = '/web/issues/'


# Set the context processors used by RequestContext objects: 
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
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.sessions',
    'django.contrib.markup',
    'debug_toolbar', # comment out in production!!
    'edemocracy.gamelogic',
    'edemocracy.profiles',
    'edemocracy.api',
    'edemocracy.web',
    'edemocracy.voting',
    'edemocracy.issues_content',
    # There are currently 2 tests failing for registration due to template 
    # inheritance. 
	'registration',
    'piston',
)
# comment out in production
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# loggin setup:
# (see: http://simonwillison.net/2008/May/22/debugging/ )
# and python docs

LOG_FILE_NAME = os.path.join(PROJECT_PATH, "edemocracy_log.txt")

logging.basicConfig(
    level = logging.DEBUG,
    format = '%(asctime)s %(levelname)s %(message)s',
    filename = LOG_FILE_NAME,
)

ACCOUNT_ACTIVATION_DAYS = 1

try:
    from settings_local import *
except ImportError:
    print "Create your local settings_local.py settings file with password sensitive information ect"
    # Re-raise the import error. The server should not run!
    raise
