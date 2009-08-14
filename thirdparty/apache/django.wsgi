import os
import sys

from os.path import abspath , dirname , join
# redirect prints to error log
sys.stdout = sys.stderr


os.environ['DJANGO_SETTINGS_MODULE'] = 'thirdparty.settings'
sys.path.append(abspath(join(dirname(__file__), "../../")))
sys.path.append(abspath(join(dirname(__file__), "../../external_apps")))
sys.path.append(abspath(join(dirname(__file__), "../")))



import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
