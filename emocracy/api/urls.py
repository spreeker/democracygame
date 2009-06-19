from django.conf.urls.defaults import *
from django.conf import settings
from piston.resource import Resource
from piston.authentication import OAuthAuthentication

from piston.emitters import Emitter
from piston.emitters import JSONEmitter

from emocracy.api.handlers import IssueHandler
from emocracy.api.handlers import IssueListHandler
from emocracy.api.handlers import UserListHandler
from emocracy.api.handlers import UserHandler
from emocracy.api.handlers import VoteHandler
from emocracy.api.handlers import VoteListHandler

# Emitter registrered to set wrong mime-type for visibility purposes
# just comment these two lines out for production
#if settings.DEBUG:
#    Emitter.unregister(JSONEmitter)
#    Emitter.register('json', JSONEmitter, 'text/html; charset=utf-8')
    
auth = OAuthAuthentication(realm='emo.buhrer.net')

issues = Resource(handler=IssueListHandler, authentication=auth)
issue = Resource(handler=IssueHandler, authentication=auth)
users = Resource(handler=UserListHandler, authentication=auth)
user = Resource(handler=UserHandler, authentication=auth)
votes = Resource(handler=VoteListHandler, authentication=auth)
vote = Resource(handler=VoteHandler, authentication=auth)

urlpatterns = patterns('',
    url(r'^issues/$', issues , name="api_issues" ),
    url(r'^issues/(?P<id>\d+)/$', issue ,  name="api_issue"),
    url(r'^users/$', users , name="api_users" ),
    url(r'^users/(?P<id>\d+)/$', user , name="api_user" ),
    url(r'^votes/$', votes, name="api_votes" ),
    url(r'^votes/(?P<id>\d+)/$', vote , name="api_vote" ),
)
