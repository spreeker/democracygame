from django.conf.urls.defaults import *

from oauth_consumer.views import *

urlpatterns = patterns('oauth_consumer.views',
    url(r'^$',
        view=main,
        name='oauth_main'),
    
    url(r'^auth/$',
        view=auth,
        name='oauth_auth'),

    url(r'^callback/$',
        view=return_,
        name='oauth_return'),
  
    url(r'^return/$',
        view=return_,
        name='oauth_return'),
  
    url(r'^list/$',
        view=friend_list,
        name='oauth_friend_list'),
    
    url(r'^clear/$',
        view=unauth,
        name='oauth_unauth'),
)
