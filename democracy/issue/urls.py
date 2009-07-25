from django.conf.urls.defaults import *
from issue.models import Issue

urlpatterns = patterns('issue.views',
    url(r'^vote/(?P<issue_id>\d+)$', 'record_vote', name='vote' ),
    url(r'^multiply/(?P<issue_id>\d+)$', 'record_multiply', name='multiply' ),
    url(r'^(?P<sortorder>\w+)/$', 'issue_list' , name='issue_list'),
)
