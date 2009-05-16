import settings
from django.conf.urls.defaults import *
from views import IssueResource, IssueCollection 
from views import IssueVoteCollection
from views import IssueTagCollection
from views import IssueVoteUserResource
from views import VoteResource 
from views import VoteCollection
from views import UserResource
from views import UserCollection
from views import TagResource


urlpatterns = patterns('api.views',
    url(r'^issues/$', IssueCollection(), name = 'api_issue'),
    url(r'^issues/(?P<pk>\d+)/$', IssueResource(), name = 'api_issue_pk'),
    url(r'^issues/(?P<pk>\d+)/votes/$', IssueVoteCollection(), name = 'api_issue_pk_vote'),  
    url(r'^issues/(?P<pk>\d+)/tags/$', IssueTagCollection(), name = 'api_issue_pk_tag'),  
    url(r'^issues/(?P<issue_pk>\d+)/for_user/(?P<user_pk>\d+)/$', IssueVoteUserResource(), name = 'api_issue_pk_vote_user'),
    url(r'^votes/$', VoteCollection(), name = 'api_vote'),
    url(r'^votes/(?P<pk>\d+)/$', VoteResource(), name = 'api_vote_pk'),
    url(r'^users/$', UserCollection(), name = 'api_user'),
    url(r'^users/(?P<pk>\d+)/$', UserResource(), name = 'api_user_pk'),
    url(r'^tags/(?P<pk>\d+)/$', TagResource(), name = 'api_tag_pk'),
)
