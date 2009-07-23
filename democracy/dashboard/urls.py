from django.conf.urls.defaults import *

from issue.models import Issue

from democracy.dashboard.views import index

urlpatterns = patterns('',
    url(r'^issue/vote/(?P<issue_id>\d+)$', 'dashboard.views.record_vote', name='vote' ),
    url(r'^issue/multiply/(?P<issue_id>\d+)$', 'dashboard.views.record_multiply', name='multiply' ),
    url(r'^$', index , name='dashboard'),
)
