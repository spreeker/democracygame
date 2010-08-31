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
        self.i = Issue( title="test" , body="test", user=u )
        self.i.save()

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
        urls.append(reverse('my_issues', args=['popular']))
        urls.append(reverse('my_issues', args=['controversial']))
        urls.append(reverse('my_issues', args=['for']))
        urls.append(reverse('my_issues', args=['against']))

        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code , 200)

    def test_anonymous_votes(self):
        url = reverse("vote", args=[self.i.pk] )
        response = self.client.post(url, direction=1)
        self.assertEqual(response.status_code, 302)
        #annonymous sessions are not testable YET.

        #url = reverse('issue_list' , args=["new"])
        #can't acces an anonymous session.. *sigh* BUG 17-8-2009
        #so we just check response content.
        #response = self.client.get(url)

        #self.assertContains(response, "<div class=\"for\"> 1</div>")
