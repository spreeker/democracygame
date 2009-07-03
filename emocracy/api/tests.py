from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import simplejson
from django.conf import settings
from django.core.urlresolvers import reverse
from piston import oauth
from piston.models import Consumer, Token
from piston.forms import OAuthAuthenticationForm

import urllib, base64

from emocracy.api.handlers import IssueVotesHandler
from emocracy.api.handlers import VoteHandler 
from emocracy.gamelogic.tests import TestActions
from emocracy.gamelogic import actions
from emocracy.voting.models import Issue

#from test_project.apps.testapp.models import TestModel, ExpressiveTestModel, Comment, InheritedModel
#from test_project.apps.testapp import signals

class APIMainTest(TestActions):
    """ We inherit from TestActions from gameactions.tests so the
    DB get filled with some more testusers and issues to test the api with.
    The game tests will be executed ass wel which must PASS before you test the api.
    """

    def setUp(self):
        super(APIMainTest , self).setUp()

        self.auth_string = 'Basic %s' % base64.encodestring('test1:testpw').rstrip()

        if hasattr(self, 'init_delegate'):
            self.init_delegate()
        
    def tearDown(self):
        super( APIMainTest , self ).tearDown()

    # do an autheniticated request?

# This is derived from the piston tests 
# modified for our api

class OAuthTests(APIMainTest):
    signature_method = oauth.OAuthSignatureMethod_HMAC_SHA1()

    def setUp(self):
        super(OAuthTests, self).setUp()

        self.consumer = Consumer(name='Test Consumer', description='Test', status='accepted')
        self.consumer.generate_random_codes()
        self.consumer.save()

    def tearDown(self):
        super(OAuthTests, self).tearDown()
        self.consumer.delete()

    def test_handshake(self):
        '''Test the OAuth handshake procedure
        '''
        oaconsumer = oauth.OAuthConsumer(self.consumer.key, self.consumer.secret)

        # Get a request key...
        request = oauth.OAuthRequest.from_consumer_and_token(oaconsumer,
                http_url='http://testserver/oauth/request_token/'
                )
        request.sign_request(self.signature_method, oaconsumer, None)
        response = self.client.get('/oauth/request_token/', request.parameters)
        oatoken = oauth.OAuthToken.from_string(response.content)

        token = Token.objects.get(key=oatoken.key, token_type=Token.REQUEST)
        self.assertEqual(token.secret, oatoken.secret)

        # Simulate user authentication...
        self.failUnless(self.client.login(username='test1', password='testpw'))
        request = oauth.OAuthRequest.from_token_and_callback(token=oatoken,
                callback='http://printer.example.com/request_token_ready',
                http_url='http://testserver/oauth/authorize/')
        request.sign_request(self.signature_method, oaconsumer, oatoken)

        # Request the login page
# TODO: Parse the response to make sure all the fields exist
#        response = self.client.get('/api/oauth/authorize', {
#            'oauth_token': oatoken.key,
#            'oauth_callback': 'http://printer.example.com/request_token_ready',
#            })

        response = self.client.post('/oauth/authorize/', {
            'oauth_token': oatoken.key,
            'oauth_callback': 'http://printer.example.com/request_token_ready',
            'csrf_signature': OAuthAuthenticationForm.get_csrf_signature(settings.SECRET_KEY, oatoken.key),
            'authorize_access': 1,
            })

        # Response should be a redirect...
        self.assertEqual(302, response.status_code)
        self.assertEqual('http://printer.example.com/request_token_ready?oauth_token='+oatoken.key, response['Location'])

        # Obtain access token...
        request = oauth.OAuthRequest.from_consumer_and_token(oaconsumer, token=oatoken,
                http_url='http://testserver/oauth/access_token/')
        request.sign_request(self.signature_method, oaconsumer, oatoken)
        response = self.client.get('/oauth/access_token/', request.parameters)

        oa_atoken = oauth.OAuthToken.from_string(response.content)
        atoken = Token.objects.get(key=oa_atoken.key, token_type=Token.ACCESS)
        self.assertEqual(atoken.secret, oa_atoken.secret)


class IssueVotesHandlerTest(APIMainTest):
    """
    testing the IssueVoteHandler which can be accessed anonymously
    we are only seeing very few votes in our test data but you will get the idea
    how other votes values are returned.
    """

    def test_gone_issue_votes(self):
        expected = 'Gone'
        url = reverse("api_issue_votes" , args=[9999999] )  # get votes for non excistent issue 
        result = self.client.get(url).content
        self.assertEquals(expected, result)

    def test_issue_votes(self):
        expected = """{
    "1": 1
}"""
        issue2 = Issue.objects.get( title = "issue2" )
        url = reverse("api_issue_votes" , args=[issue2.pk] ) # the first issue has 2 votes?
        result = self.client.get(url).content
        self.assertEqual(expected , result)
        vote_func = actions.role_to_actions[self.profiles[0].role]['vote'] 
        vote_func( self.users[0] , issue2 , -1 , False)
    
        expected = """{
    "1": 1
    "-1": 1
}"""


class VoteHandlerTest(APIMainTest):
    """ test voting.
        TODO who to do oauth requests??
    """

    def test_duplicate_vote(self):
        pass

    def test_non_exsitent_vote(self):
        pass

    def test_vote_own_issue(self):
        pass

    def test_vote(self):
        pass



class UserHandlerTest( APIMainTest ):
    
    def test_get_users(self):
        expected = """[
    {
        "username": "test1", 
        "ranking": 3, 
        "score": 11, 
        "resource_uri": "%(r1)s"
    }, 
    {
        "username": "test2", 
        "ranking": 3, 
        "score": 11, 
        "resource_uri": "%(r2)s"
    }, 
    {
        "username": "test3", 
        "ranking": 3, 
        "score": 11, 
        "resource_uri": "%(r3)s"
    }
]""" % {"r1" :  reverse('api_user' , args=[self.users[0].id]) , 
        "r2" :  reverse('api_user' , args=[self.users[1].id]) , 
        "r3" :  reverse('api_user' , args=[self.users[2].id]) , 
        }

        url = reverse( "api_users" )
        result = self.client.get(url).content        
        #print result
        self.assertEqual( expected , result )

    def test_get_user(self):
        user = User.objects.get( username = 'test1' )
        expected = """[
    {
        "username": "test1", 
        "ranking": 3, 
        "score": 11, 
        "resource_uri": "%(r1)s"
    }
]""" % {"r1" :  reverse('api_user' , args=[self.users[0].id]) } 

        url = reverse( "api_user" , args=[user.pk] ) 
        result = self.client.get(url).content
        self.assertEqual( expected , result )


class IssueHandlerTest( APIMainTest ):
   
    def init_delegate(self):
        self.issue1 = Issue.objects.get( title = "issue1")
        self.issue2 = Issue.objects.get( title = "issue2")
        self.issue3 = Issue.objects.get( title = "issue3")
        print self.issue1.id , self.issue2.id , self.issue3.id
 
    def test_read_issues(self):
        expected = """[
    {
        "body": "issue3issue3issue3issue3issue3issue3issue3issue3issue3issue3", 
        "title": "issue3", 
        "url": "example.com", 
        "source_type": "url", 
        "owner": {
            "username": "test3", 
            "resource_uri": "%(ru3)s"
        }, 
        "time_stamp": "%(t3)s", 
        "resource_uri": "%(ri3)s"
    }, 
    {
        "body": "issue2issue2issue2issue2issue2issue2issue2issue2issue2issue2", 
        "title": "issue2", 
        "url": "example.com", 
        "source_type": "url", 
        "owner": {
            "username": "test2", 
            "resource_uri": "%(ru2)s"
        }, 
        "time_stamp": "%(t2)s", 
        "resource_uri": "%(ri2)s"
    }, 
    {
        "body": "issue1issue1issue1issue1issue1issue1issue1issue1issue1issue1", 
        "title": "issue1", 
        "url": "example.com", 
        "source_type": "url", 
        "owner": {
            "username": "test1", 
            "resource_uri": "%(ru1)s"
        }, 
        "time_stamp": "%(t1)s", 
        "resource_uri": "%(ri1)s"
    }
]""" % {"t1" : self.issue1.time_stamp.strftime("%Y-%m-%d %H:%M:%S"),
        "t2" : self.issue2.time_stamp.strftime("%Y-%m-%d %H:%M:%S"),
        "t3" : self.issue3.time_stamp.strftime("%Y-%m-%d %H:%M:%S"),
        "ru1" : reverse("api_user" , args=[self.users[0].id]) , 
        "ru2" : reverse("api_user" , args=[self.users[1].id]) , 
        "ru3" : reverse("api_user" , args=[self.users[2].id]) , 
        "ri1" : reverse("api_issue" , args=[self.issue1.id] ) ,
        "ri2" : reverse("api_issue" , args=[self.issue2.id] ) ,
        "ri3" : reverse("api_issue" , args=[self.issue3.pk] ) ,
        }

        url = reverse( "api_issues" )
        result = self.client.get( url ).content
        #print result
        #rf = open( "r.txt" , 'w' )
        #cf = open( "c.txt" , 'w' )
        ## open the files in a file diff viewer to see result differences
        #rf.write(result)
        #cf.write(expected)
        self.assertEqual( expected , result )

        def test_read_issue(self):
            expected = """[
    {
        "body": "issue1issue1issue1issue1issue1issue1issue1issue1issue1issue1", 
        "title": "issue1", 
        "url": "example.com", 
        "source_type": "url", 
        "owner": {
            "username": "test1", 
            "resource_uri": "/api/v0/user/4/"
        }, 
        "time_stamp": "%(t3)s", 
        "resource_uri": "/api/v0/issue/4/"
    }
]""" % {"t1" : self.issue1.time_stamp.strftime("%Y-%m-%d %H:%M:%S") }

            url = reverse( "api_issue" , args=[self.issue1.pk] )
            result = self.client.get( url )
            self.assertEqual( expected , result )


#    def test_singlexml(self):
#        obj = TestModel.objects.all()[0]
#        expected = '<?xml version="1.0" encoding="utf-8"?>\n<response><test1>None</test1><test2>None</test2></response>'
#        result = self.client.get('/api/entry-%d.xml' % (obj.pk,),
#                HTTP_AUTHORIZATION=self.auth_string).content
#        self.assertEquals(expected, result)

   
#class AbstractBaseClassTests(MainTests):
#    def init_delegate(self):
#        self.ab1 = InheritedModel()
#        self.ab1.save()
#        self.ab2 = InheritedModel()
#        self.ab2.save()
#        
#    def test_field_presence(self):
#        result = self.client.get('/api/abstract.json',
#                HTTP_AUTHORIZATION=self.auth_string).content
#                
