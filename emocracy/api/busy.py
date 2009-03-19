import httplib

from oauth import oauth
# This file will evolve into some utility functions to talk to the Emocracy
# API from Python (not necessarily through Django). Based on Django snippets
# http://www.djangosnippets.org/snippets/655/
# http://www.djangosnippets.org/snippets/1353/

# ------------------------------------------------------------------------------
# -- default settings ----------------------------------------------------------

# Make sure not to use PLAINTEXT signature method over an unencrypted connection
signature_method = oauth.OAuthSignatureMethod_PLAINTEXT()
#signature_method = oauth.OAuthSignatureMethod_HMAC_SHA1()
# The settings for an oauth consumer (available after registration with the
# emocracy project):
CONSUMER_KEY = 'conrado'
CONSUMER_SECRET = 'conrado'
consumer = oauth.OAuthConsumer(CONSUMER_KEY, CONSUMER_SECRET)
# The following should be changed to emocracy proper:
SERVER = '127.0.0.1'
PORT = '8000'
# The following should move to using https:
#ACCES_TOKEN_URL = 'http://127.0.0.1:8000/oauth/acces_token/'
ACCES_TOKEN_URL = '/oauth/acces_token/'
REQUEST_TOKEN_URL = '/oauth/request_token/'
#REQUEST_TOKEN_URL = 'http://127.0.0.1:8000/oauth/request_token/'
AUTHORIZATION_URL = 'http://127.0.0.1:8000/authorize/'

connection = httplib.HTTPConnection(SERVER, PORT)

# ------------------------------------------------------------------------------
# -- utility / helper functions for oauth --------------------------------------

def fetch_request_token():
    oauth_request = oauth.OAuthRequest.from_consumer_and_token(consumer,
        http_url = REQUEST_TOKEN_URL)
    oauth_request.sign_request(signature_method, consumer, None)

    URL = oauth_request.to_url()
    connection.request('GET', URL[3:]) # THIS IS A HACK!
    oauth_response = connection.getresponse()
    content = oauth_response.read()
    # some debug mess:
    if oauth_response.status == 500:
        f = open("error.html", "w")
        f.write(content)
        f.close()
        print "Server error"
    else:
        print "No problem"
    return oauth.OAuthToken.from_string(content)

def fetch_access_token(request_token):
    # takes a request token and exchanges it for an accces token
    oauth_request = oauth.OAuthRequest.from_consumer_and_token(consumer,
        token = request_token, http_url = ACCES_TOKEN_URL)
    oauth_request.sign_request(signature_method, consumer, request_token)
    URL = oauth_request.to_url()[3:]
    print "->", URL
    connection.request(oauth_request.http_method, URL)
    oauth_response = connection.getresponse()
    content = oauth_response.read()

    if oauth_response.status == 500:
        f = open("error_acces.html", "w")
        f.write(content)
        f.close()
        print "Server error"
    else:
        print "No problem"

    print "joY!"
    return oauth.OAuthToken.from_string(content)
    

def authorize():
    pass



if __name__ == "__main__":
    request_token = fetch_request_token()
    print request_token
    acces_token = fetch_access_token(request_token)
    print access_token
    