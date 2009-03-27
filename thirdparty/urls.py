

import os
from django.conf.urls.defaults import *


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

import settings

urlpatterns = patterns('',
    # Example:
    # (r'^thirdparty/', include('thirdparty.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Development stuff, media served by django itself. Remove for a real
    # Emocracy installation (and have Apache handle media).
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name':'login.html'}, name = 'login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'template_name':'logout.html'}, name = 'logout'),
    (r'^', include('thirdparty.web.urls')),
    (r'^media/(.*)', 'django.views.static.serve', {
        'document_root' : os.path.join(settings.PROJECT_PATH, 'media')
    }),

    # Uncomment the next line to enable the admin:
    (r'^admin/(.*)', admin.site.root),
)
