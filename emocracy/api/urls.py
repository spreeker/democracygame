import settings
from django.conf.urls.defaults import *
from views import IssueResource, IssueCollection
from views import VoteResource, VoteCollection
from views import UserResource, UserCollection


urlpatterns = patterns('api.views',
    url(r'^issue/$', IssueCollection(), name = 'api_issue'),
    url(r'^issue/(?P<pk>\d+)/$', IssueResource(), name = 'api_issue_pk'),
    url(r'^vote/$', VoteCollection(), name = 'api_vote'),
    url(r'^vote/(?P<pk>\d+)/$', VoteResource(), name = 'api_vote_pk'),
    url(r'^user/$', UserCollection(), name = 'api_user'),
    url(r'^user/(?P<pk>\d+)/$', UserResource(), name = 'api_user_pk'),
)