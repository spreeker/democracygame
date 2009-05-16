import oauth.oauth as oauth
import httplib

# An easier to use OAuth library forked from python-oauth

# OAuthURLS - request token, authorize, and access token URLs on service provider
class OAuthURLS(object):
    request_token_url = None
    authorization_url = None
    access_token_url = None

    def __init__(self, request_token_url=None, authorization_url=None, access_token_url=None):
        self.request_token_url = request_token_url
        self.authorization_url = authorization_url
        self.access_token_url = access_token_url

# OAuthClient - for the consumer
class OAuthEasyClient(object):
    consumer = None
    urls = None
    signature_method = None
    connection = None

    def __init__(self, oauth_consumer, oauth_urls, signature_method, server, port=80):
        self.consumer = oauth_consumer
        self.urls = oauth_urls
        self.signature_method = signature_method
        self.connection = httplib.HTTPConnection(server, port)

    def get_request_token(self, http_method=oauth.HTTP_METHOD, parameters=None):
        request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, \
          http_method=http_method, http_url=self.urls.request_token_url, \
          parameters=parameters)
        request.sign_request(self.signature_method, self.consumer, None)

        self.connection.request(request.http_method, request.http_url, headers=request.to_header())
        response = self.connection.getresponse()
        return oauth.OAuthToken.from_string(response.read())

    def get_access_token(self, request_token):
        request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, token=request_token, http_url=self.urls.access_token_url)
        request.sign_request(self.signature_method, self.consumer, request_token)

        self.connection.request(request.http_method, request.http_url, headers=request.to_header())
        response = self.connection.getresponse()
        return oauth.OAuthToken.from_string(response.read())

    def get_authorization_url(self, request_token, callback=None, parameters=None):
        request = oauth.OAuthRequest.from_token_and_callback(request_token, callback, parameters=parameters, http_url=self.urls.authorization_url)
        return request.to_url()

    def get_resource(self, resource_url, access_token):
        request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, token=access_token, http_url=resource_url)
        request.sign_request(self.signature_method, self.consumer, access_token)
        self.connection.request(request.http_method, request.http_url, headers=request.to_header())
        response = self.connection.getresponse()
        return response.read()
