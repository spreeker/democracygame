import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'edemocracy.settings'
sys.path.append('/var/git/emo')
sys.path.append('/var/git/emo/edemocracy')
sys.path.append('/var/git/emo/external_apps')


import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
