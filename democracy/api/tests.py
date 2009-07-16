from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import simplejson
from django.conf import settings
from django.core.urlresolvers import reverse
from piston import oauth
from piston.models import Consumer, Token
from piston.forms import OAuthAuthenticationForm

import urllib, base64

from democracy.api.handlers import IssueVotesHandler
from democracy.api.handlers import VoteHandler 
from democracy.gamelogic.tests import TestActionData
from democracy.gamelogic.models import MultiplyIssue
from democracy.gamelogic import actions
from democracy.issue.models import Issue

#from test_project.apps.testapp.models import TestModel, ExpressiveTestModel, Comment, InheritedModel
#from test_project.apps.testapp import signals

class APIMainTest(TestActionData):
    """ We inherit from TestActionData from gameactions.tests so the
    DB get filled with some more testusers and issues to test the api with.
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
    """ 
    OAuthTest Does oauth handshake test and gives derived test classes tests the possibility
    to do OAuth resource requests. 
    """
    signature_method = oauth.OAuthSignatureMethod_HMAC_SHA1()

    def setUp(self):
        super(OAuthTests, self).setUp()

        self.consumer = Consumer(name='Test Consumer', description='Test', status='accepted')
        self.consumer.generate_random_codes()
        self.consumer.save()
        self.oa_atoken = None 
        self.test_handshake()

    def tearDown(self):
        super(OAuthTests, self).tearDown()
        self.consumer.delete()

    def do_oauth_request(self, url , parameters = {} , http_method = 'POST' ):
        
        oaconsumer = oauth.OAuthConsumer(self.consumer.key, self.consumer.secret)

        request = oauth.OAuthRequest.from_consumer_and_token(
                oaconsumer, 
                http_method=http_method, 
                token=self.oa_atoken,
                http_url='http://testserver%s' % url )
        
        request.parameters.update( parameters )
        request.sign_request(self.signature_method, oaconsumer, self.oa_atoken )
        
        if http_method == 'POST':
            response = self.client.post( url, request.parameters )
        else :
            response = self.client.get( url, request.parameters )

        return response

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
        # save the acces token so we can do oauth requests
        self.oa_atoken = oa_atoken


class IssueVotesHandlerTest(APIMainTest):
    """
    testing the IssueVoteHandler which can be accessed anonymously
    returns json with vote_kind : vote_count for that kind of vote.
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


class VoteHandlerTest( OAuthTests ):
    """ test voting.

        we do signed oauth requests , acces token is created by
        OAuthTests.

        auhtenticated user is test1 , oa_atoken is for user test1.
    """

    def test_duplicate_vote(self):
        """ 
        Duplicate voting should not be allowed.
        In the creation of parent class TestActions we created 3 issues
        each user has his own vote on its own issue. 
        """
        parameters = {
                'vote' : 1 ,
                'issue' : Issue.objects.get( title = "issue1").pk ,
                }
        url = reverse( "api_vote" )
        response = self.do_oauth_request( url , parameters )
        # conflict / Duplicate
        self.assertEqual( 409 , response.status_code )

    def test_non_exsitent_issue(self):
        parameters = {
                'vote' : -1 ,
                'issue' : 99999 ,
                }
        url = reverse( "api_vote" )
        response = self.do_oauth_request( url , parameters )

        self.assertEqual( 400 , response.status_code )

    def test_vote(self):
        """
        Do a negative vote on issue 3. 
        this should succeed. with a 201 CREATED status.
        """
        parameters = {
                'vote' : -1 ,
                'issue' : Issue.objects.get( title = "issue3").pk ,
                }

        url = reverse( "api_vote" )
        response = self.do_oauth_request( url , parameters )
        self.assertEqual(201, response.status_code)

    def test_read_votes(self):
        # there should be only one vote for user test1
        from democracy.voting.models import Vote
        vote = Vote.objects.get( user = self.users[0].id ) 
        issue1 = Issue.objects.get( title = "issue1")
        url = reverse ( 'api_vote' ) 
        response = self.do_oauth_request(url , http_method='GET' ) 
        expected = """[
    {
        "vote": 1, 
        "time_stamp": "%(t1)s", 
        "user_uri": "%(ru1)s", 
        "issue_uri": "%(ri1)s", 
        "keep_private": false
    }
]""" % {"t1" : vote.time_stamp.strftime("%Y-%m-%d %H:%M:%S"),
        "ru1" : reverse("api_user" , args=[self.users[0].id]) , 
        "ri1" : reverse("api_issue" , args=[issue1.id] ) ,
        }
        self.assertEqual( expected , response.content )
        self.assertEqual( 200 , response.status_code )


class AnonymousUserHandlerTest( APIMainTest ):
    
    def test_get_users(self):
        expected = """[
    {
        "username": "test1", 
        "ranking": 3, 
        "score": 12, 
        "resource_uri": "%(r1)s"
    }, 
    {
        "username": "test2", 
        "ranking": 3, 
        "score": 12, 
        "resource_uri": "%(r2)s"
    }, 
    {
        "username": "test3", 
        "ranking": 3, 
        "score": 12, 
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
        "score": 12, 
        "resource_uri": "%(r1)s"
    }
]""" % {"r1" :  reverse('api_user' , args=[self.users[0].id]) } 

        url = reverse( "api_user" , args=[user.pk] ) 
        result = self.client.get(url).content
        self.assertEqual( expected , result )

class UserHandlerTest ( OAuthTests ):
    """
    Do an oauth request for you own private data
    """
    
    def test_get_user_data(self):
        url = reverse( 'api_user' , args=[self.users[0].pk] )
        response = self.do_oauth_request( url , http_method = 'GET' )

        expected = """{
    "username": "test1", 
    "ranking": 3, 
    "score": 12, 
    "role": "opinion leader", 
    "email": "test1@example.com", 
    "resource_uri": "%(ur1)s"
}""" % { "ur1" : reverse( 'api_user' , args=[self.users[0].pk]) }

        self.assertEqual( expected , response.content )


class IssueHandlerTest( APIMainTest ):
   
    def init_delegate(self):
        self.issue1 = Issue.objects.get( title = "issue1")
        self.issue2 = Issue.objects.get( title = "issue2")
        self.issue3 = Issue.objects.get( title = "issue3")
 
    def test_read_issues(self):
        expected = """[
    {
        "body": "issue1issue1issue1issue1issue1issue1issue1issue1issue1issue1", 
        "title": "issue1", 
        "url": "example.com", 
        "source_type": "website", 
        "user": {
            "username": "test1", 
            "resource_uri": "%(ru1)s"
        }, 
        "time_stamp": "%(t1)s", 
        "resource_uri": "%(ri1)s"
    }, 
    {
        "body": "issue2issue2issue2issue2issue2issue2issue2issue2issue2issue2", 
        "title": "issue2", 
        "url": "example.com", 
        "source_type": "website", 
        "user": {
            "username": "test2", 
            "resource_uri": "%(ru2)s"
        }, 
        "time_stamp": "%(t2)s", 
        "resource_uri": "%(ri2)s"
    }, 
    {
        "body": "issue3issue3issue3issue3issue3issue3issue3issue3issue3issue3", 
        "title": "issue3", 
        "url": "example.com", 
        "source_type": "website", 
        "user": {
            "username": "test3", 
            "resource_uri": "%(ru3)s"
        }, 
        "time_stamp": "%(t3)s", 
        "resource_uri": "%(ri3)s"
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
        # open the files in a file diff viewer to see result differences
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
        "user": {
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


class MultiplyHandlerTest( OAuthTests ):
    """
    do oauth request to get you own multiplies. 
    """ 

    def test_get_own_multiplies(self):
        issue2 = Issue.objects.get( title = "issue2" )
        self.do_multiply( self.users[0] ,  issue2 )
        self.do_multiply( self.users[1] ,  issue2 )
        multiply_vote = MultiplyIssue.objects.get( user = self.users[0] )

        url = reverse( "api_multiplies" )
        response = self.do_oauth_request( url , http_method="GET" )
        expected = """[
    {
        "time_stamp": "%(ts)s", 
        "issue": {
            "resource_uri": "%(iu)s"
        }, 
        "user": {
            "resource_uri": "%(ou)s"
        }, 
        "resource_uri": "%(mu)s"
    }
]""" % {"ou" : reverse( "api_user" , args=[ self.users[0].pk] ) , 
        "ts" : multiply_vote.time_stamp.strftime("%Y-%m-%d %H:%M:%S") ,
        "iu" : reverse( "api_issue" , args=[issue2.pk] ) , 
        "mu" : reverse( "api_multiply" , args=[multiply_vote.id] ) , 
        }
        result = response.content 
        self.assertEqual( expected , result )
   
    def test_post_multiply(self):
        issue2 = Issue.objects.get( title = "issue2" )
        parameters = {
            'issue' : issue2.pk
        }
        url = reverse( "api_multiplies" )       
        response = self.do_oauth_request( url , parameters = parameters ) 
        self.assertEqual( 201 , response.status_code )

    def test_post_own_multiply(self):
        issue1 = Issue.objects.get( title = "issue1" )
        parameters = {
            'issue' : issue1.pk
        }
        url = reverse( "api_multiplies" )       
        response = self.do_oauth_request( url , parameters = parameters ) 
        self.assertEqual( 400 , response.status_code )
 

class AnonymousMultiplyHandlerTest( APIMainTest ):
    

    def test_get_multiplies (self):
        #remember only users 1 and 2 can do multiplies
        issue1 = Issue.objects.get( title="issue1" )
        issue2 = Issue.objects.get( title="issue2" )

        self.do_multiply( self.users[0], issue2 )
        self.do_multiply( self.users[1], issue1 )
        
        multiply_vote1 = MultiplyIssue.objects.get( user=self.users[0] )
        multiply_vote2 = MultiplyIssue.objects.get( user=self.users[1] )

        url = reverse( 'api_multiplies' )
        response = self.client.get( url )

        expected = """[
    {
        "time_stamp": "%(ts2)s", 
        "issue": {
            "resource_uri": "%(iu1)s"
        }, 
        "user": {
            "resource_uri": "%(ou2)s"
        }, 
        "resource_uri": "%(mu2)s"
    }, 
    {
        "time_stamp": "%(ts1)s", 
        "issue": {
            "resource_uri": "%(iu2)s"
        }, 
        "user": {
            "resource_uri": "%(ou1)s"
        }, 
        "resource_uri": "%(mu1)s"
    }
]""" % {"ou1" : reverse( "api_user" , args=[ self.users[0].pk] ) , 
        "ts1" : multiply_vote1.time_stamp.strftime("%Y-%m-%d %H:%M:%S") ,
        "iu1" : reverse( "api_issue" , args=[issue1.pk] ) , 
        "mu1" : reverse( "api_multiply" , args=[multiply_vote1.id] ) , 
        "ou2" : reverse( "api_user" , args=[ self.users[1].pk] ) , 
        "ts2" : multiply_vote2.time_stamp.strftime("%Y-%m-%d %H:%M:%S") ,
        "iu2" : reverse( "api_issue" , args=[issue2.pk] ) , 
        "mu2" : reverse( "api_multiply" , args=[multiply_vote2.id] ) ,
        }
        #print response
        #rf = open( "r.txt" , 'w' )
        #cf = open( "c.txt" , 'w' )
        # open the files in a file diff viewer to see result differences
        #rf.write(response.content)
        #cf.write(expected)
           
        self.assertEqual ( expected , response.content )

