from django.conf.urls.defaults import *
from issue.models import Issue
from django.views.decorators.cache import cache_page

from views import issue_list

urlpatterns = patterns('issue.views',
    url(r'^vote/(?P<issue_id>\d+)$', 'record_vote', name='vote' ),
    url(r'^multiply/(?P<issue_id>\d+)$', 'record_multiply', name='multiply' ),
    url(r'^publish/(?P<issue_id>\d+)$', 'publish_issue', name='publish'),
    #url(r'^(?P<sortorder>\w+)/$', cache_page(issue_list, 1*10) , name='issue_list'),
    url(r'^(?P<sortorder>\w+)/$', issue_list , name='issue_list'),
)
