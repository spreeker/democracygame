from django.core.urlresolvers import reverse 
from django.contrib.auth.models import User
from django.test import TestCase 

from gamelogic.tests import TestActionData 

from issue.models import Issue
from voting.models import Vote


class IndexTest(TestActionData):
    """
    smoke test the basic pages
    """ 
    def setUp(self):
        super(IndexTest , self).setUp()
        #u = User.objects.create_user("test", "s@p.com", "test")
        #self.i = Issue(title="test", body="test", user=u)
        #self.i.save()

    def tearDown(self):
        super(IndexTest ,self).tearDown()

    def test_smoke_test(self):
        """ smoke test loading the basic pages should just work"""
        urls = [ ]
        urls.append('/')
        urls.append(reverse('api_doc'))
        urls.append(reverse('laws'))
        urls.append(reverse('issue_list_user', args=['test0']))

        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code , 200)

    def test_issue_sort(self):
        """ smoke test views """
        self.client.login(username='test0', password='testpw')

        urls = [ ]
        urls.append('/')
        urls.append(reverse('my_issues_sort', args=["new"]))
        urls.append(reverse('my_issues_sort', args=['popular']))
        urls.append(reverse('my_issues_sort', args=['controversial']))
        urls.append(reverse('my_issues_sort', args=['for']))
        urls.append(reverse('my_issues_sort', args=['against']))

        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code , 200)
            #print response.content

    def test_anonymous_votes(self):
        #TODO ANYMOUS SESSION STORE SUCKS.
        #self.client.login(username='test', password='test')
        self.client.get('/')
        issue1 = Issue.objects.get(title="issue1")  
        url = reverse("vote", args=[issue1.pk] )
        response = self.client.post(url, direction=1)
        self.assertEqual(response.status_code, 302)
        #annonymous sessions are not testable YET.
        url = reverse('issue_list' , args=["new"])
        #so we just check response content.
        response = self.client.get(url)
        session = self.client.session

        #self.assertContains(response, "<div class=\"for\"> 1</div>")

    ##TODO test_vote? test_post issue?
