# By Thijs Coenen for the Emocracy project october 2008
import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to

# TODO 'namespace' the url names (prepend the app name)

urlpatterns = patterns('web.views',
    # urls that go with viewing of Issues
    url(r'^issues/for_user/(?P<username>\w+)/$', 'issues_list_user', name = 'web_issues_for_user'),
    url(r'^issues/for_tag/(?P<tag_pk>\d+)/$', 'issue_list_tag', name = 'web_issue_list_tag'),
    url(r'^issues/(?P<pk>\d+)/$', 'newdetail', name = 'web_issue_detail' ),
    url(r'^issues/$', 'issue_list', name = 'web_issue_list'),
    # helper views that deal with jQuery based voting/tagging:
    url(r'^ajax/voteform/(?P<issue_no>\d+)/$', 'voteform', name = 'web_voteform'),
    url(r'^ajax/vote/$', 'ajaxvote', name = 'web_ajaxvote'),     
    url(r'^ajax/tag/(?P<pk>\d+)/$', 'ajaxtag', name = 'add_tag'),
    url(r'^ajax/tagform/(?P<issue_pk>\d+)/$', 'tagform', name='tagform'),
    # Propose new Issues
    url(r'^propose/$', 'issue_propose', name = 'issue_propose'),
    # Show list of votes for a user.
    url(r'^votes/(?P<user_name>\w+)/$', 'vote_list_user', name = 'votes_for_user'),
    # Polling TODO : needs a clean up
    url(r'^polls/$', 'poll_list', name = 'poll_list'), # generic view
    url(r'^polls/(?P<poll_no>\d+)/result/$', 'poll_result', name = 'poll_result'), # special view, needs some calculations done
    url(r'^poll/(?P<pk>\d+)/take/$', 'poll_take', name = 'poll_take'),
    # Start of a mandate a user view
    url(r'^mandate/(?P<rep>\w+)/$', 'mandate', name = 'mandate'),
    # Start of a become candidate view
    url(r'^become_candidate/', 'become_candidate', name = 'become_candidate'),
    # Start of a tag searching function TODO : check for unicode in request paramaters,
    # which is not allowed according to Conrado...
    url(r'^search_tag/$', 'search_tag', name = 'search_tag'),
    
    # For Demo purposes: redirect all the wrong stuff to the issue_list views...
#    (r'$', redirect_to, {'url' : '/web/issue/'}),
)