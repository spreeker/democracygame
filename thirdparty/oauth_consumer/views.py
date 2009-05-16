import oauth.oauth as oauth
import httplib, time, datetime

import easyoauth
from utils import OAUTH_URLS, SIGNATURE_METHOD, SERVER, PORT

try:
    import simplejson
except ImportError:
    try:
        import json as simplejson
    except ImportError:
        try:
            from django.utils import simplejson
        except:
            raise "Requires either simplejson, Python 2.6 or django.utils!"

from django.http import *
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse

from oauth_consumer.utils import *



def main(request):
    if request.user.is_anonymous():
        return HttpResponseRedirect(reverse('login'))
    else:
        if getattr(request.user.get_profile(), 'access_token'):
            return HttpResponseRedirect(reverse('top_level_menu'))
        else:
            return render_to_response('authorize.html',
                RequestContext(request, {}))

def unauth(request):
    response = HttpResponseRedirect(reverse('oauth_main'))
    p = request.user.get_profile()
    p.access_token.delete()
    p.save()
    request.session.clear()
    return response

def auth(request):
    "/auth/"
    consumer = oauth.OAuthConsumer(CONSUMER_KEY, CONSUMER_SECRET)
    client = easyoauth.OAuthEasyClient(consumer, OAUTH_URLS, SIGNATURE_METHOD, SERVER, PORT)
    token = client.get_request_token()
    auth_url = client.get_authorization_url(token, CALLBACK_URL)
    response = HttpResponseRedirect(auth_url)
    request.session['unauthed_token'] = token.to_string()
    return response

def return_(request):
    "/return/"
    consumer = oauth.OAuthConsumer(CONSUMER_KEY, CONSUMER_SECRET)
    client = easyoauth.OAuthEasyClient(consumer, OAUTH_URLS, SIGNATURE_METHOD, SERVER, PORT)
    unauthed_token = request.session.get('unauthed_token', None)
    if not unauthed_token:
        return HttpResponse("No un-authed token cookie")
    token = oauth.OAuthToken.from_string(unauthed_token)   
    if token.key != request.GET.get('oauth_token', 'no-token'):
        return HttpResponse("Something went wrong! Tokens do not match")
    access_token = client.get_access_token(token)
    response = HttpResponseRedirect(reverse('oauth_friend_list'))
    if not request.user.is_anonymous():
        p = request.user.get_profile()
        p.access_token = access_token.to_string()
        p.save()
    request.session['access_token'] = access_token.to_string()
    return response

def friend_list(request):
    consumer = oauth.OAuthConsumer(CONSUMER_KEY, CONSUMER_SECRET)
    client = easyoauth.OAuthEasyClient(consumer, OAUTH_URLS, SIGNATURE_METHOD, SERVER, PORT)
    users = []
    
    if not request.user.is_anonymous():
        p = request.user.get_profile()
        access_token = p.access_token
        print access_token
    else:
        access_token = request.session.get('access_token', None)
    if not access_token:
        return HttpResponse("You need an access token!")
    token = oauth.OAuthToken.from_string(access_token)   
    
    # Check if the token works on Twitter
    auth = client.get_resource('/api/issues/', token)
    return HttpResponse(auth)
    #return render_to_response('oauth_test.html', {'context': auth})
