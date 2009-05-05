

import settings
from django.conf.urls.defaults import *


urlpatterns = patterns('thirdparty.web.views',
    url(r'^$', 'top_level_menu', name="top_level_menu"),
    url(r'^pop/$', 'issues_list_popular', name="issues_list_popular"),
    url(r'^hot/$', 'issues_list_hottest', name="issues_list_hottest"),
    url(r'^new/$', 'issues_list_newest', name="issues_list_newest"),
#    url(r'^add/$', 'issues_add_issue', name="issues_add_issue"),
    url(r'^user/(?P<pk>\d+)/$', 'user_details', name="user_details"),
    url(r'^login/$', 'user_login', name="user_login"),
    url(r'^logout/$', 'user_logout', name="user_logout"),
    url(r'^(?P<pk>\d+)/$', 'issues_issue_detail', name="issues_issue_detail"),
    url(r'^(?P<pk>\d+)/vote/?P<vote>\w+$', 'issues_issue_vote', name="issues_issue_vote"),

)
