

import settings
from django.conf.urls.defaults import *


urlpatterns = patterns('',
    url(r'^popular/$', 'issues_list_popular', name="issues_list_popular"),
)
