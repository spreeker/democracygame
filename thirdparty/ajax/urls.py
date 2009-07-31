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

)
