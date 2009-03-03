import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to


urlpatterns = patterns('',
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name' : 'accounts/login.html' }, name = 'login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'template_name' : 'accounts/logged_out.html'}, name = 'logout'),
    url(r'^register/$', 'emocracy.accounts.views.register_user', name = 'register'),
    url(r'^password_reset/$', 'emocracy.accounts.views.email_new_password', name = 'email_new_password'),
    url(r'^profile/(?P<username>\w+)/$', 'emocracy.accounts.views.userprofile_show', name = 'userprofile'),
    url(r'^change_description/$', 'emocracy.accounts.views.change_description', name = 'change_description'),
    url(r'^search_user/$', 'emocracy.accounts.views.search_user', name = 'search_user'),
#    (r'$', redirect_to, {'url' : '/web/issues/'}),
)