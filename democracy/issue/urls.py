from django.conf.urls.defaults import *
from issue.models import Issue
from django.views.decorators.cache import cache_page

from tagging.views import tagged_object_list

from views import issue_list, issue_list_user

urlpatterns = patterns('issue.views',
    url(r'^vote/(?P<issue_id>\d+)$', 'record_vote', name='vote' ),
    url(r'^multiply/(?P<issue_id>\d+)$', 'record_multiply', name='multiply' ),
    url(r'^tag/(?P<issue_id>\d+)$', 'tag_issue', name='tag_issue' ),
    url(r'^with/tag/(?P<tag>[^/]+)/$', 'issue_list' , name='issue_with_tag'),
    url(r'^publish/(?P<issue_id>\d+)$', 'publish_issue', name='publish'),
    #url(r'^(?P<sortorder>\w+)/$', cache_page(issue_list, 1*10) , name='issue_list'),
    url(r'^(?P<sortorder>\w+)/$', issue_list , name='issue_list'),
    url(r'^by/(?P<username>\w+)/$', issue_list_user, name='issue_list_user'),
    url(r'^by/(?P<username>\w+)/(?P<sortorder>\w+)/$', issue_list_user, name='issue_list_user_sort'),

)
