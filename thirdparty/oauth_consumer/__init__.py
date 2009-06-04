import django_oauth_consumer
from django_oauth_consumer import NoAccessToken

CONSUMER_KEY = "noct"
CONSUMER_SECRET = "noct"

NAME = 'EmOAuth'

API_SERVER = 'http://emo.buhrer.net/api/'
REQUEST_TOKEN_URL = 'http://emo.buhrer.net/oauth/request_token/'
ACCESS_TOKEN_URL = 'http://emo.buhrer.net/oauth/access_token/'
AUTHORIZATION_URL = 'http://emo.buhrer.net/oauth/authorize/'
REALM = 'emo.buhrer.net'
SIGNATURE_METHOD = 'oauth.signature_method.plaintext.OAuthSignatureMethod_PLAINTEXT'


class EmoOAuthConsumerApp(django_oauth_consumer.OAuthConsumerApp):
    
    def  __init__(self,
        name=NAME,
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        request_token_url=REQUEST_TOKEN_URL,
        authorization_url=AUTHORIZATION_URL,
        access_token_url=ACCESS_TOKEN_URL,
        realm=REALM,
        signature_method=SIGNATURE_METHOD):
    
        super(EmoOAuthConsumerApp, self).__init__(
        name=name,
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        request_token_url=request_token_url,
        authorization_url=authorization_url,
        access_token_url=access_token_url,
        realm=realm,
        signature_method=signature_method)

    def store_access_token(self, request, token):
        if not request.user.is_anonymous():
            profile = request.user.get_profile()
            profile.access_token = token['oauth_token']
            profile.access_secret = token['oauth_token_secret']
            profile.save()
        else:
            request.session[self.ACCESS_TOKEN_NAME] = token

    def get_access_token(self, request):
        if not request.user.is_anonymous():
            profile = request.user.get_profile()
            if not profile.access_token:
                raise NoAccessToken()
            else:
                token = {}
                token['oauth_token'] = profile.access_token
                token['oauth_token_secret'] = profile.access_secret
                return token
        else:
            if self.ACCESS_TOKEN_NAME in request.session:
                return request.session[self.ACCESS_TOKEN_NAME]
            else:
                raise NoAccessToken()

    def get_resource(self, request, resource):
        try:
            token = self.get_access_token(request)
            return self.make_signed_req(url=resource, token=token, request=request)
        except NoAccessToken:
            return self.make_signed_req(url=resource)

    def post_resource(self, request, resource, content=None):
        if resource==None:
            return false
        try:
            token = self.get_access_token(request)
            return self.make_signed_req(url=resource, method='POST', content=content, token=token, request=request)
        except NoAccessToken:
            raise

    def post_vote(self, request, vote_data):
        """
        Posts a vote to Emocracy Service Provider.

        `vote_data` should be a dictionary:
            { 'issue' : integer,
              'keep_private' : boolean,
              'vote' : integer,  # valid values -1, 1, 10-19 (see emocracy docs)
            }
        """
        api_url = API_SERVER+'votes/'
        response = self.post_resource(request, api_url, content=vote_data)
        return response

    def get_issue_list(self, request):
        api_url = API_SERVER+'issues/'
        return self.get_resource(request, api_url)

