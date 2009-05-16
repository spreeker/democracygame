from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.authentication import OAuthAuthentication
from piston.emitters import Emitter
from piston.emitters import JSONEmitter

from emocracy.api.handlers import IssueHandler
from emocracy.api.handlers import IssueListHandler
from emocracy.api.handlers import UserListHandler
from emocracy.api.handlers import UserHandler

# Emitter registrered to set wrong mime-type for visibility purposes
# just comment these two lines out for production
Emitter.unregister(JSONEmitter)
Emitter.register('json', JSONEmitter, 'text/html; charset=utf-8')

auth = OAuthAuthentication(realm='emo.buhrer.net')

issues = Resource(handler=IssueListHandler, authentication=auth)
issue = Resource(handler=IssueHandler, authentication=auth)
users = Resource(handler=UserListHandler, authentication=auth)
user = Resource(handler=UserHandler, authentication=auth)

urlpatterns = patterns('',
    url(r'^issues/$', issues),
    url(r'^issues/(?P<id>\d+)/$', issue),
    url(r'^users/$', users),
    url(r'^users/(?P<id>\d+)/$', user),
)
