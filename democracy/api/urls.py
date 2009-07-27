from django.conf.urls.defaults import *
from django.conf import settings
from django.views.decorators.cache import cache_page

from piston.resource import Resource
from piston.authentication import OAuthAuthentication
from piston.authentication import HttpBasicAuthentication

from piston.emitters import Emitter
from piston.emitters import JSONEmitter

from api.handlers import IssueHandler
from api.handlers import UserHandler
from api.handlers import VoteHandler
from api.handlers import MultiplyHandler
from api.handlers import IssueVotesHandler
from api.handlers import IssueList
from api.handlers import TagCloudHandler 
from api.handlers import TagHandler


from api.doc import documentation_view

auth = OAuthAuthentication(realm='d.preeker.net')

# Emitter registrered to set wrong mime-type for visibility purposes
# just comment these lines out for production
# setting the authtication to basic so you can test in the browser the
# api responses

if settings.DEBUG:
    Emitter.unregister(JSONEmitter)
    Emitter.register('json', JSONEmitter, 'text/html; charset=utf-8')
    auth = HttpBasicAuthentication(realm='m.buhrer.net')

issue = Resource(handler=IssueHandler, authentication=auth )
user = Resource(handler=UserHandler, authentication=auth )
vote = Resource(handler=VoteHandler, authentication=auth )
multiply = Resource(handler=MultiplyHandler, authentication=auth )
issuelist = Resource(handler=IssueList, authentication=auth)
issue_votes = Resource(handler=IssueVotesHandler)
tag_cloud = Resource(handler=TagCloudHandler)
issues_with_tags = Resource(handler=TagHandler)

#NOTE we need page and tag vars in url and not as parameter because of caching.
#django cache does not cache urls with parameters.
#currently basic middleware cacheing works , granular cache_page gives problems.

urlpatterns = patterns('',
    # returns paginated issues public
    url(r'^issue/$', issue, name="api_issues" ),
    url(r'^issue\.page/(?P<page>\d+)/$', issue, ),
    # returns specific issue public
    url(r'^issue/(?P<id>\d+)/$', issue,  name="api_issue"),
    # return votes on specific issue public
    url(r'^issue/(?P<id>\d+)/votes/$', issue_votes, name="api_issue_votes" ),
    # return list of issues , popular , new , controversial
    url(r'^issues/(?P<sortorder>\w+)/', issuelist, name="api_sort_order" ),
    url(r'^issues/(?P<sortorder>\w+)\.page/(?P<page>\d+)/$', issuelist,),
    # return users public
    url(r'^users\.page/(?P<page>\d+)/$', user, ),
    url(r'^users/$', user, name="api_users" ),
    # return specific user and stats NOT PUBLIC 
    url(r'^user/(?P<id>\d+)/$', user , name="api_user" ),
    # oauth: GET votes of user , POST vote for an user
    url(r'^vote/$', vote, name="api_vote" ),
    url(r'^vote/(?P<id>\d+)/$', vote, name="api_read_vote" ),
    url(r'^vote/(?P<id>\d+)\.page/(?P<page>\d+)/$', vote, ),
    # view multiplies
    url(r'^multiply/$', multiply, name='api_multiplies' ),
    url(r'^multiply\.page/(?P<page>\d+)/$', multiply, ),
    # multiply an issue 
    url(r'^multiply/(?P<issue>)\d+/$', multiply, name='api_multiply' ),
    url(r'^doc/$', documentation_view, name="api_doc" ),
    url(r'^tagcloud/', tag_cloud, name='api_tagcloud'),
    url(r'^issues.tags/(?P<tags>[^/]+)/', issues_with_tags, ),
)
