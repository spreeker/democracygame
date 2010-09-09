import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to

from django.views.generic.simple import direct_to_template
from django.contrib.auth import views as auth_views

#from registration.views import activate
from profiles.views import activate
from profiles.views import userprofile_show
from profiles.views import change_description
from profiles.views import compare_votes_to_user
from profiles.views import record_vote_on_user

from registration.views import register

# TODO: fix indentation

urlpatterns = patterns('',
    # views dealing with users.
    url(r'^compare_votes_to_user/(?P<username>\w+)/$', compare_votes_to_user,
        name='compare_votes_to_user',),
    url(r'^vote/(?P<user_id>\d+)$', record_vote_on_user, name='vote_user'),
    
    # profile and account management urls.

    # Activation keys get matched by \w+ instead of the more specific
    # [a-fA-F0-9]{40} because a bad activation key should still get to the view;
    # that way it can return a sensible "invalid key" message instead of a
    # confusing 404.
    url(r'^activate/(?P<activation_key>\w+)/$', activate, name='registration_activate'),
    url(r'^login/$', auth_views.login, {'template_name': 'profiles/login.html'},
       name='auth_login'),
    url(r'^logout/$', auth_views.logout, {'template_name': 'profiles/logout.html'},
       name='logout'),
    url(r'^password/change/$', auth_views.password_change, name='auth_password_change'),
    url(r'^password/change/done/$', auth_views.password_change_done,
       name='auth_password_change_done'),
    url(r'^password/reset/$', auth_views.password_reset,
       name='auth_password_reset'),
    url(r'^password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
       auth_views.password_reset_confirm,
       name='auth_password_reset_confirm'),
    url(r'^password/reset/complete/$', auth_views.password_reset_complete,
       name='auth_password_reset_complete'),
    url(r'^password/reset/done/$', auth_views.password_reset_done,
       name='auth_password_reset_done'),
    url(r'^register/$',
       register,
       {'backend': 'registration.backends.default.DefaultBackend' } ,
       name='registration_register'),
    url(r'^register/complete/$', direct_to_template,
       {'template': 'registration/registration_complete.html'},
       name='registration_complete'),
    url(r'^userprofile/(?P<username>\w+)/$', userprofile_show,
        name='userprofile',),
    url(r'^changedescription/$', change_description,
        name='change_description',),
     )
