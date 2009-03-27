from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^minimal/', include('minimal.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/(.*)', admin.site.root),

    (r'^login/$', 'django.contrib.auth.views.login', {'template_name' : 'login.html'}),
    (r'^logout/$', 'django.contrib.auth.views.logout', {'template_name' : 'logout.html'}),
    (r'^web/', include('minimal.web.urls')),
)
