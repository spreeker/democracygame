import settings
from django.conf.urls.defaults import *
from views import IssueResource, IssueCollection, IssueVoteCollection
from views import VoteResource, VoteCollection
from views import UserResource, UserCollection


urlpatterns = patterns('api.views',
    url(r'^issues/$', IssueCollection(), name = 'api_issue'),
    url(r'^issues/(?P<pk>\d+)/$', IssueResource(), name = 'api_issue_pk'),
    url(r'^issues/(?P<pk>\d+)/votes/$', IssueVoteCollection(), name = 'api_issue_pk_vote'),  
    url(r'^votes/$', VoteCollection(), name = 'api_vote'),
    url(r'^votes/(?P<pk>\d+)/$', VoteResource(), name = 'api_vote_pk'),
    url(r'^users/$', UserCollection(), name = 'api_user'),
    url(r'^users/(?P<pk>\d+)/$', UserResource(), name = 'api_user_pk'),
)