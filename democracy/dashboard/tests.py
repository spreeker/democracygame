from django.core.urlresolvers import reverse 
from django.contrib.auth.models import User
from django.test import TestCase 
from gamelogic.tests import TestActionData 

class IndexTest(TestCase):
    """
    smoke test the basic pages
    """ 
    def test_smoke_test(self):
        """ smoke test loading the basic pages should just work"""
        urls = [ ]
        urls.append('/')
        urls.append(reverse('api_doc'))
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code , 200)

