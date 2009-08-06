"""
implementation of oauth consumer app.
Here we wrap the specific oauth resources with the
oauth authentication headers.
"""
import logging
import django_oauth_consumer
from django_oauth_consumer import NoAccessToken

from django.conf import settings
from django.utils import simplejson as json

CONSUMER_KEY = settings.CONSUMER_KEY
CONSUMER_SECRET = settings.CONSUMER_SECRET

NAME = 'DemOAuth'

SERVER = settings.DEMOCRACY_API_SERVER
API_SERVER = SERVER + "api/v0/"

REQUEST_TOKEN_URL = '%soauth/request_token/' % SERVER
ACCESS_TOKEN_URL = '%soauth/access_token/' % SERVER
AUTHORIZATION_URL = '%soauth/authorize/' % SERVER
REALM = settings.REALM
SIGNATURE_METHOD = 'oauth.signature_method.plaintext.OAuthSignatureMethod_PLAINTEXT'


class DemoOAuthConsumerApp(django_oauth_consumer.OAuthConsumerApp):
    """ the Oauth consumer parent class does the actual connecting to the api
        server
    """
    def  __init__(self,
        name=NAME,
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        request_token_url=REQUEST_TOKEN_URL,
        authorization_url=AUTHORIZATION_URL,
        access_token_url=ACCESS_TOKEN_URL,
        realm=REALM,
        signature_method=SIGNATURE_METHOD):

        super(DemoOAuthConsumerApp, self).__init__(
        name=name,
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        request_token_url=request_token_url,
        authorization_url=authorization_url,
        access_token_url=access_token_url,
        realm=realm,
        signature_method=signature_method)

        self.response = None

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

    def ld(self):
        """Load data - parse json from last request"""
        data = self.response.read()
        try :
            decoded_json = json.loads(data)
        except ValueError :
            decoded_json = []
            logging.debug( """
                        loading of json data goes wrong. Probably the Service provider is not yet
                        accepting your oauth consumer key. Or some ohter local oauth configuration
                        is wrong
                        """)
            logging.debug( str(data))

        return decoded_json

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
              'vote' : integer,  # valid values -1, 1, 10-19 (see democracy docs)
            }
        """
        api_url = '%svote/' % API_SERVER
        self.response = self.post_resource(request, api_url, content=vote_data)
        return self.response.status

    # public? cached?
    def get_issue_list(self, request):
        tempuser = request.user
        from django.contrib.auth.models import AnonymousUser
        request.user = AnonymousUser()
        api_url = '%sissue/' % API_SERVER
        self.response = self.get_resource(request, api_url)
        request.user = tempuser
        return self.ld()

    # public? cached?
    def get_issue(self, request, issue_no):
        api_url = '%sissue/%s/' % (API_SERVER, issue_no)
        self.response = self.get_resource(request, api_url)
        return self.ld()
    def get_issue_json(self, request, issue_no):
        tempuser = request.user
        from django.contrib.auth.models import AnonymousUser
        request.user = AnonymousUser()
        api_url = '%sissue/%s/' % (API_SERVER, issue_no)
        self.response = self.get_resource(request, api_url)
        request.user = tempuser
        return self.response
    
    def get_issue_votes(self, request, issue_no):
        api_url = '%sissue/%s/votes/' % (API_SERVER, issue_no)
        self.response = self.get_resource(request, api_url)
        return self.ld()
    
    def get_issue_votes_json(self, request, issue_no):
        api_url = '%sissue/%s/votes/' % (API_SERVER, issue_no)
        self.response = self.get_resource(request, api_url)
        return self.response

    def get_issue_vote(self, request, issue_no):
        api_url = '%svote/%s/' % (API_SERVER, issue_no)
        self.response = self.get_resource(request, api_url)
        return self.ld()

    def get_issue_vote_json(self, request, issue_no):
        api_url = '%svote/%s/' % (API_SERVER, issue_no)
        self.response = self.get_resource(request, api_url)
        return self.response

    def get_issue_votes_user(self, request):
        api_url = '%svote/' % API_SERVER
        self.response = self.get_resource(request, api_url)
        return self.ld()

    def get_user(self, request, user_no):
        api_url = '%suser/%s/' % (API_SERVER, user_no)
        self.response = self.get_resource(request, api_url)
        return self.ld() 

    def post_issue(self, request, issue_data):
        api_url = '%sissue/' % API_SERVER
        self.response = self.post_resource(request, api_url, content=issue_data)
        f = open('/Users/thijscoenen/Desktop/out.html', 'w')
        f.write(self.response.read())
        f.close()
        
        return self.response.status
