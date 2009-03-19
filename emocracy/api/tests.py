import unittest
from django.test.client import Client

import time
from oauth_provider.models import Consumer, Resource, Token
import oauth

#c = Client()
#response = c.get("http://127.0.0.1:8000/api/oauth_test/")
#print response.status_code

class AuthTest(unittest.TestCase):
    def testone(self):
        # this unittest tries to grab the /api/oauth_test/ resource
        # Define the resource:
        resource = Resource(url = '/api/oauth_test/', name = 'oauth_test')
        resource.save()
        print Resource.objects.all()
        # Create an oauth consumer:
        CONSUMER_KEY = 'dpf43f3p2l4k3l03'
        CONSUMER_SECRET = 'kd94hf93k423kf44'
        consumer = Consumer(key = CONSUMER_KEY, secret = CONSUMER_SECRET, name = 'test consumer')
        consumer.save()
        print Consumer.objects.all()
        # Get a request token:
        p = {
            'oauth_consumer_key' : CONSUMER_KEY,
            'oauth_signature_method' : 'PLAINTEXT',
            'oauth_signature' : '%s&' % CONSUMER_SECRET,
            'oauth_timestamp' : str(int(time.time())),
            'oauth_nonce' : 'requestnonce',
            'oauth_version' : '1.0',
            'scope' : 'oauth_test',
        }
        c = Client()
        response = c.get("/oauth/request_token/", p)
        
        print Token.objects.all()
        self.assertEquals(int(response.status_code), 200)
        print response.status_code 
        print response.content
        print response.GET
        
