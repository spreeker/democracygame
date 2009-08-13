from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('ajax.views',
    url(r'^vote/cast/$',
        view='ajax_vote_cast',
        name='ajax_vote_cast'),

    url(r'^issue/(?P<issueid>\d+)/$',
        view='ajax_get_issue',
        name='ajax_get_issue'),

    url(r'^issue/(?P<issueid>\d+)/votes/$',
        view='ajax_get_issue_votes',
        name='ajax_get_issue_votes'),

    url(r'^issues/(?P<sortorder>\w+)/$',
        view='ajax_get_issues_list_ordered',
        name='ajax_get_issues_list_ordered'),

    url(r'^issues/(?P<sortorder>\w+)\.page/(?P<page>\d+)/$',
        view='ajax_get_issues_list_ordered',
        name='ajax_get_issues_list_ordered'),
)
