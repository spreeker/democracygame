from django.conf.urls.defaults import *

from oauth_consumer.views import *
from oauth_consumer.consumer import EmoOAuthConsumerApp

emoauth = EmoOAuthConsumerApp()

urlpatterns = patterns('',
    url(r'^auth/', emoauth.need_authorization, name=emoauth.NEEDS_AUTH_VIEW_NAME),
    url(r'^success/(?P<oauth_token>.*)/', emoauth.success_auth, name=emoauth.SUCCESS_VIEW_NAME),
    url(r'$', 'oauth_consumer.views.index', name='index'),
)
