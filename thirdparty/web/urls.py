

import settings
from django.conf.urls.defaults import *


urlpatterns = patterns('thirdparty.web.views',
    url(r'^$', 'interface', name="top_level_menu"),
    url(r'^issue/(?P<issueid>\d+)/$', 'issue_ajax', name="issue_ajax"),
    url(r'^myvote/(?P<issueid>\d+)/$', 'myvote_ajax', name="myvote_ajax"),
    url(r'^totals/(?P<issueid>\d+)/$', 'vote_totals_ajax', name="vote_totals_ajax"),
    url(r'^add/(?P<issue_no>)/$', 'issues_add_issue', name="issues_edit_issue"),
    url(r'^add/$', 'issues_add_issue', name="issues_add_issue"),
    url(r'^login/$', 'user_login', name="user_login"),
                       #url(r'^logout/$', 'user_logout', name="user_logout"),
    url(r'^error/$', 'issues_submit_error', name="issues_submit_error"),
    url(r'^debug/$', 'debug', name="debug"),
)
