import os
from django.conf.urls.defaults import *

from django.views.generic.simple import redirect_to

from django.contrib import admin
admin.autodiscover()

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

    (r'^accounts/', include('emocracy.accounts.urls')),
#    (r'$', redirect_to, {'url' : '/web/issues/'}) # for demo purposes
)
