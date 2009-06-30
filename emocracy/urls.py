import os
from django.conf.urls.defaults import *

from django.views.generic.simple import redirect_to

from django.contrib import admin
admin.autodiscover()

from piston.authentication import oauth_request_token, oauth_user_auth, oauth_access_token
import settings

urlpatterns = patterns('',
    (r'^web/', include('emocracy.web.urls')),
    (r'^api/', include('api.urls')),
    # Example:
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/(.*)', admin.site.root),
    # Development stuff, media served by django itself. Remove for a real
    # Emocracy installation (and have Apache handle media).
    (r'^media/(.*)', 'django.views.static.serve', {
        'document_root' : os.path.join(settings.PROJECT_PATH, 'media')
    }),

    (r'^oauth/request_token/$', oauth_request_token),
    (r'^oauth/authorize/$', oauth_user_auth),
    (r'^oauth/access_token/$', oauth_access_token),

    (r'^profile/', include('emocracy.profiles.urls')),

    (r'^i18n/', include('django.conf.urls.i18n')),
    # For Demo purposes: redirect all the wrong stuff to the issue_list views...
    #(r'$', redirect_to, {'url' : '/web/issues/'}),
)
