from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.test import TestCase 
from gamelogic.tests import TestActionData 

class TestIndex(TestCase):
    """ smoke test the basic pages """
    def test_smoketest(self):
        """ smoke test loading the basic pages should just work"""
        urls = [ ]
        urls.append(reverse('dashboard'))
        urls.append(reverse('api_doc'))
        #urls.append("/")
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code , 200)

class TestDashBoardActions(TestActionData):

    pass    

