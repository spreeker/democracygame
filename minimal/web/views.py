import httplib, urlparse

from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.http import QueryDict

from oauth import oauth

signature_method = oauth.OAuthSignatureMethod_PLAINTEXT()

CONSUMER_KEY = 'MINIMAL'
CONSUMER_SECRET = 'MINIMAL'
consumer = oauth.OAuthConsumer(CONSUMER_KEY, CONSUMER_SECRET)

# HARD CODED FOR NOW:
SERVER = '127.0.0.1'
PORT = 8000
connection = httplib.HTTPConnection(SERVER, PORT)

REQUEST_TOKEN_URL = 'http://127.0.0.1:8000/oauth/request_token/'
ACCES_TOKEN_URL = 'http://127.0.0.1:8000/oauth/access_token/'
AUTHORIZE_URL = 'http://127.0.0.1:8000/oauth/authorize/'

def get_request_token():
    oauth_request = oauth.OAuthRequest.from_consumer_and_token(consumer, 
        http_url = REQUEST_TOKEN_URL)
    oauth_request.sign_request(signature_method, consumer, None)

    URL = oauth_request.to_url()
    parts = urlparse.urlsplit(URL)
    relative_URL = "%s?%s" % (parts[2], parts[3]) 

    connection.request('GET', relative_URL)
    oauth_response = connection.getresponse()
    content = oauth_response.read()
    print "\n\n" + content + "\n\n"
    return oauth.OAuthToken.from_string(content)

def get_acces_token():
    pass





@login_required
def index(request):
    request_token = get_request_token()
    
    print request_token.key
    
    parameters = QueryDict({}).copy()
    parameters['oauth_token'] = request_token.key
#    parameters['ouath_callback'] = 'http://127.0.0.1:8080/succes/'
    return HttpResponseRedirect(AUTHORIZE_URL + '?' + parameters.urlencode())
    
    return render_to_response(
        'web/index.html', {
            'token' : request_token,
        }
    )
    