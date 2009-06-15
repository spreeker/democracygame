import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'thirdparty.settings'
sys.path.append('/var/git/emo')
sys.path.append('/var/git/emo/external_apps')
sys.path.append('/var/git/emo/thirdparty')


import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
