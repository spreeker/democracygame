

import settings
from django.conf.urls.defaults import *


urlpatterns = patterns('thirdparty.web.views',
    url(r'^popular/$', 'issues_list_popular', name="issues_list_popular"),
    url(r'^(?P<pk>\d+)/$', 'issues_issue_detail', name="issues_issue_detail"),
    url(r'^(?P<pk>\d+)/vote/$', 'issues_issue_vote', name="issues_issue_vote"),

)
