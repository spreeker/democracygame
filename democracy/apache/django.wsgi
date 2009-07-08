import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'democracy.settings'
sys.path.append('/var/git/emo')
sys.path.append('/var/git/emo/democracy')
sys.path.append('/var/git/emo/external_apps')


import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
