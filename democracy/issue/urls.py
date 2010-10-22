from django.conf.urls.defaults import *
from issue.models import Issue
from django.views.decorators.cache import cache_page
from tagging.views import tagged_object_list

urlpatterns = patterns('issue.views',
    url(r'^vote/(?P<issue_id>\d+)$', 'record_vote', name='vote' ),
    url(r'^multiply/(?P<issue_id>\d+)$', 'record_multiply', name='multiply' ),
    url(r'^laws/(?P<sortorder>\w+)$', 'issues_list_laws', name='laws_sorted' ),
    url(r'^laws/$', 'issues_list_laws', name='laws' ),

    url(r'^tag/(?P<issue_id>\d+)$', 'tag_issue', name='tag_issue' ),
    url(r'^with/tag/(?P<tag>[^/]+)/$', 'issue_list' , name='issue_with_tag'),
    url(r'^publish/(?P<issue_id>\d+)$', 'publish_issue', name='publish'),

    url(r'^by/(?P<username>\w+)/$', 'issue_list_user', name='issue_list_user'),
    url(r'^by/(?P<username>\w+)/(?P<sortorder>\w+)/$', 'issue_list_user', name='issue_list_user_sort'),
    url(r'^made/by/me/(?P<sortorder>\w+)/$', 'my_issue_list', name='my_issues_sort'),
    url(r'^made/by/me/$', 'my_issue_list' , name='my_issues'),

    url(r'^title/(?P<title>[-\w]+)/$', 'single_issue', name='single_issue'),

    url(r'^search/$', 'search_issue', name='search_issue'),
    url(r'^xhr_search/$', 'xhr_search_issue', name='xhr_search_issue'),

    url(r'^(?P<sortorder>\w+)/$', 'issue_list' , name='issue_list'),
    #url(r'^(?P<sortorder>\w+)/$', cache_page(issue_list, 1*10) , name='issue_list'),
)
