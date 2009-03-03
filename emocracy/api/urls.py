import settings
from django.conf.urls.defaults import *
from views import IssueResource, IssueCollection


urlpatterns = patterns('api.views',
    url(r'^issue/$', IssueCollection(), name = 'api_issue'),
    url(r'^issue/(?P<pk>\d+)/$', IssueResource(), name = 'api_issue_pk'),
)