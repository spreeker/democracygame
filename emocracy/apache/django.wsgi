import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'emocracy.settings'
sys.path.append('/var/git/emo')
sys.path.append('/var/git/emo/emocracy')
sys.path.append('/var/git/emo/external_apps')


import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
