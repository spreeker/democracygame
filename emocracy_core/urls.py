# By Thijs Coenen for the Emocracy project october 2008
import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to


urlpatterns = patterns('',
    # urls that go with viewing of Issues/Votables
    url(r'^issue/for_user/(?P<username>\w+)/$', 'emocracy_core.views.issues_list_user', name = 'issues_for_user'),
    url(r'^issue/for_tag/(?P<tag_pk>\d+)/$', 'emocracy_core.views.issue_list_tag', name = 'issue_list_tag'),
    url(r'^issue/(?P<pk>\d+)/$', 'emocracy_core.views.newdetail', name = 'issue_detail' ),
    url(r'^issue/$', 'emocracy_core.views.issue_list', name = 'issue_list'),
    # helper views that deal with jQuery based voting/tagging.
    url(r'^ajax/voteform/(?P<issue_no>\d+)/$', 'emocracy_core.views.voteform', name = 'voteform'),
    url(r'^ajax/vote/$', 'emocracy_core.views.ajaxvote', name = 'ajaxvote'),     
    # TODO : clean up the view function that does tagging - it no longer needs
    # to deal with normal web form based input.
    url(r'^ajax/tag/(?P<pk>\d+)/$', 'emocracy_core.views.ajaxtag', name = 'add_tag'),
    
    url(r'ajax/tagform/(?P<votable_pk>\d+)/$', 'emocracy_core.views.tagform', name='tagform'),
    # Propose new Issues
    url(r'^propose/$', 'emocracy_core.views.issue_propose', name = 'issue_propose'),
    # Show list of votes for a user.
    url(r'^votes/(?P<user_name>\w+)/$', 'emocracy_core.views.vote_list_user', name = 'votes_for_user'),
    # Polling TODO : needs a clean up
    url(r'^polls/$', 'emocracy_core.views.poll_list', name = 'poll_list'), # generic view
    url(r'^polls/(?P<poll_no>\d+)/result/$', 'emocracy_core.views.poll_result', name = 'poll_result'), # special view, needs some calculations done
    url(r'^poll/(?P<pk>\d+)/take/$', 'emocracy_core.views.poll_take', name = 'poll_take'),
    # Start of a mandate a user view
    url(r'^mandate/(?P<rep>\w+)/$', 'emocracy_core.views.mandate', name = 'mandate'),
    # Start of a become candidate view
    url(r'^become_candidate/', 'emocracy_core.views.become_candidate', name = 'become_candidate'),
    # Start of a tag searching function TODO : check for unicode in request paramaters,
    # which is not allowed according to Conrado...
    url(r'^search_tag/$', 'emocracy_core.views.search_tag', name = 'search_tag'),
    
    # For Demo purposes: redirect all the wrong stuff to the issue_list views...
#    (r'$', redirect_to, {'url' : '/web/issue/'}),
)