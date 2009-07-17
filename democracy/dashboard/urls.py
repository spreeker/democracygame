from django.conf.urls.defaults import *

from issue.models import Issue

from democracy.dashboard.views import index

urlpatterns = patterns('',
    url(r'^dashboard/vote/', 'dashboard.views.vote', name='vote' ),
    url(r'^dashboard/', index , name='dashboard'),
)
