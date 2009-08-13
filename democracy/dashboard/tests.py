from django.core.urlresolvers import reverse 
from django.contrib.auth.models import User
from django.test import TestCase 
from gamelogic.tests import TestActionData 
from issue.models import Issue

class IndexTest(TestCase):
    """
    smoke test the basic pages
    """ 
    def setUp(self):
        super(IndexTest , self).setUp()
        u = User.objects.create_user("test","s@p.com","test")
        i = Issue( title="test" , body="test", user=u )
        i.save()

    def tearDown(self):
        super( IndexTest , self ).tearDown()


    def test_smoke_test(self):
        """ smoke test loading the basic pages should just work"""
        urls = [ ]
        urls.append('/')
        urls.append(reverse('api_doc'))
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code , 200)

    def test_dashboard_test(self):
        """ smoke test views """
        self.assertEquals(
            self.client.login(username='test', password='test'), True) 

        urls = [ ]
        urls.append('/')
        urls.append(reverse('my_issues', args=["new"]))
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code , 200)


