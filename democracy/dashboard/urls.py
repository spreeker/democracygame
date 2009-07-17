from django.conf.urls.defaults import *

from issue.models import Issue

from democracy.dashboard.views import index

urlpatterns = patterns('',
    url(r'^dashboard/issue/vote/(?P<issue_id>\d+)', 'dashboard.views.record_vote', name='vote' ),
    url(r'^dashboard/', index , name='dashboard'),
)
