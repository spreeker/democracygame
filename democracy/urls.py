import os
from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

from piston.authentication import oauth_request_token
from piston.authentication import oauth_user_auth
from piston.authentication import oauth_access_token

from django.conf import settings

urlpatterns = patterns('',
    (r'^api/v0/', include('api.urls')),
    (r'^dashboard/', include('dashboard.urls')),
    (r'^issue/', include('issue.urls')),

    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/(.*)', admin.site.root),

    # Development stuff, media served by django itself.
    # in procution have Apache handle media.
    (r'^media/(.*)', 'django.views.static.serve', {
        'document_root' : os.path.join(settings.PROJECT_PATH, 'media')
    }),
    #
    (r'^oauth/request_token/$', oauth_request_token),
    (r'^oauth/authorize/$', oauth_user_auth),
    (r'^oauth/access_token/$', oauth_access_token),
    #
    (r'^profile/', include('profiles.urls')),
    (r'^i18n/', include('django.conf.urls.i18n')),
    # 
    url(r'^$' , 'issue.views.issue_list', name="index"),
)

if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^rosetta/', include('rosetta.urls')),
    )
