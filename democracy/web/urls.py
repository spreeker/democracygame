# By Thijs Coenen for the Emocracy project october 2008
import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to

# TODO 'namespace' the url names (prepend the app name)

urlpatterns = patterns('web.views',
    # urls that go with viewing of Issues
    url(r'^issues/for_user/(?P<username>\w+)/$', 'issues_list_user', name = 'web_issues_for_user'),
    url(r'^issues/for_tag/(?P<tag_pk>\d+)/$', 'issue_list_tag', name = 'web_issue_list_tag'),
    url(r'^issues/(?P<pk>\d+)/$', 'issue_detail', name = 'web_issue_detail' ),
    url(r'^issues/$', 'list_issues', name = 'web_issue_list'),
    # helper views that deal with jQuery based voting/tagging:
    url(r'^ajax/voteform/(?P<issue_no>\d+)/$', 'voteform', name = 'web_voteform'),
    url(r'^ajax/vote/$', 'ajaxvote', name = 'web_ajaxvote'),     
    url(r'^ajax/tag/(?P<pk>\d+)/$', 'ajaxtag', name = 'web_ajaxtag'),
    url(r'^ajax/tagform/(?P<issue_pk>\d+)/$', 'tagform', name='web_tagform'),
    # Propose new Issues
    url(r'^propose/$', 'issue_propose', name = 'web_issue_propose'),
    url(r'^propose/(?P<issue_no>\d+)/$', 'issue_propose', name = 'web_issue_edit'),
    # Show list of votes for a user.
    url(r'^votes/(?P<user_name>\w+)/$', 'vote_list_user', name = 'web_votes_for_user'),

    # Start of a tag searching function TODO : check for unicode in request paramaters,
    # which is not allowed according to Conrado...
    url(r'^search_tag/$', 'search_tag', name = 'web_search_tag'),
)
