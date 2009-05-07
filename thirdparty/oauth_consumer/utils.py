import oauth
from django.conf import settings

import easyoauth
import httplib


SERVER = getattr(settings, 'OAUTH_SERVER', 'emo.preeker.net')
PORT = getattr(settings, 'OAUTH_PORT', 80)

SIGNATURE_METHOD = oauth.OAuthSignatureMethod_PLAINTEXT()

OAUTH_URLS = easyoauth.OAuthURLS()
OAUTH_URLS.request_token_url = '/oauth/request_token/'
OAUTH_URLS.access_token_url = '/oauth/access_token/'
OAUTH_URLS.authorization_url = 'http://emo.preeker.net/oauth/authorize/'

CALLBACK_URL = 'http://emo.buhrer.net/oauth/callback/'
RESOURCE_URL = '/api/issues/'

CONSUMER_KEY = getattr(settings, 'CONSUMER_KEY', 'thirdparty')
CONSUMER_SECRET = getattr(settings, 'CONSUMER_SECRET', 'thirdparty')


