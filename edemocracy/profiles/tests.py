"""
Unit tests for edemocracy-profile
The tests are based on the django-registration.

These tests assume that you've completed all the prerequisites for
getting django-registration running in the default setup, to wit:

1. You have ``registration`` and ``edemocracy.profile`` in 
   your ``INSTALLED_APPS`` setting.

2. You have created all of the templates mentioned in this
   application's documentation.

3. You have added the setting ``ACCOUNT_ACTIVATION_DAYS`` to your
   settings file.

4. You have URL patterns pointing to the registration and activation
   views, with the names ``registration_register`` and
   ``registration_activate``, respectively, and a URL pattern named
   'registration_complete'.

"""

from django.test import Client, TestCase


class ClientTestRegistration(TestCase):
    fixtures = ['testdata.json']

    def test_get_view(self):
        "GET a view"
        # The data is ignored, but let's check it doesn't crash the system
        # anyway.
        data = {'var': u'\xf2'}
        response = self.client.get('/profile/register/', data)

        # Check some response details
        self.assertContains(response, 'register')
        #self.assertEqual(response.context['var'], u'\xf2')
        #self.assertEqual(response.template.name, 'GET Template')

    def test_post_a_registration(self):
        "POST registation data to a view"
        post_data = {
            'username' : 'stephan',
            'email' : 'stephan@preeker.net',
            'tos': 'on',
            'password1' : 'stephan',
            'password2' : 'stephan',
        }
        response = self.client.post('/profile/register/', post_data)

        # Check some response details , 302 mean redirect after succesfull posting of data
        self.assertEqual(response.status_code, 302)
        self.assertNotContains(response , 'errorlist' , 302)

        # You can not register twice!!
        response = self.client.post('/profile/register/', post_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response , 'errorlist' )

##import unittest
#import utils
#import views
#
#class DocStrings(unittest.TestCase):
#    
#    def test_DocStrings(self):
#        import doctest
#        doctest.testmod(modules name)
#        doctest.testmod(views)
#
#if __name__ == '__main__':
#        unittest.main()
