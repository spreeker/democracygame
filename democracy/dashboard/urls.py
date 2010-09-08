from django.conf.urls.defaults import *
from issue.models import Issue


urlpatterns = patterns('dashboard.views',
    #url(r'^my/votes/(?P<issue_id>\d+)$', 'record_vote', name='my_vote' ),
    #url(r'^my/multiplies/(?P<issue_id>\d+)$', 'dashboard.views.record_multiply', name='my_multiply' ),
    url(r'^issues/(?P<sortorder>\w+)/$', 'my_issue_list', name='my_issues'),
    url(r'^issues/$', 'my_issue_list' , name='dashboard_issues'),
    url(r'^votes/$', 'my_votes_list' , name='dashboard_votes'),
)
