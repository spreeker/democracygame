# By Thijs Coenen for the Emocracy project october 2008
import settings
from django.conf.urls.defaults import *

# TODO 'namespace' the url names (prepend the app name)

urlpatterns = patterns('',
    (r'', 'minimal.web.views.index')
)