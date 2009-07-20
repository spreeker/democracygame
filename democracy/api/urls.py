from django.conf.urls.defaults import *
from django.conf import settings
from piston.resource import Resource
from piston.authentication import OAuthAuthentication
from piston.authentication import HttpBasicAuthentication

from piston.emitters import Emitter
from piston.emitters import JSONEmitter

from democracy.api.handlers import IssueHandler
from democracy.api.handlers import UserHandler
from democracy.api.handlers import VoteHandler
from democracy.api.handlers import MultiplyHandler
from democracy.api.handlers import IssueVotesHandler


from democracy.api.doc import documentation_view

auth = OAuthAuthentication(realm='m.buhrer.net')

# Emitter registrered to set wrong mime-type for visibility purposes
# just comment these lines out for production
# setting the authtication to basic so you can test in the browser the
# api responses

if settings.DEBUG:
    Emitter.unregister(JSONEmitter)
    Emitter.register('json', JSONEmitter, 'text/html; charset=utf-8')
    auth = HttpBasicAuthentication(realm='m.buhrer.net')

issue = Resource( handler=IssueHandler, authentication=auth )
user = Resource( handler=UserHandler, authentication=auth )
vote = Resource( handler=VoteHandler, authentication=auth )
multiply = Resource( handler=MultiplyHandler , authentication=auth )

issue_votes = Resource(handler=IssueVotesHandler)

urlpatterns = patterns('',
    # returns paginated issues public
    url(r'^issue/$', issue , name="api_issues" ),
    # returns specific issue public
    url(r'^issue/(?P<id>\d+)/$', issue ,  name="api_issue"),

    # return votes on specific issue public
    url(r'^issue/(?P<id>\d+)/votes/$', issue_votes , name="api_issue_votes" ),
    # return users public
    url(r'^user/$', user , name="api_users" ),
    # return specific user and stats NOT PUBLIC 
    url(r'^user/(?P<id>\d+)/$', user , name="api_user" ),
    # oauth: GET votes of user , POST vote for an user
    url(r'^vote/$', vote , name="api_vote" ),
    # view multiplies
    url(r'^multiply/$', multiply , name='api_multiplies' ),
    # multiply an issue 
    url(r'^multiply/(?P<issue>)\d+/$', multiply , name='api_multiply' ),
    url(r'^doc/$' , documentation_view , name="api_doc" ) ,
)
