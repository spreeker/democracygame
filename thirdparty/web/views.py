# Create your views here.

import urllib2
import datetime
import time

from urllib2 import HTTPError, URLError
from django.conf import settings
from django.core import serializers
from django.utils import simplejson as json
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template import RequestContext

from settings import EMOCRACY_API_SERVER

#-----------------------------------------------------------------------------
# Some extra response codes not defined in:
# http://code.djangoproject.com/browser/django/tags/releases/1.0.2/django/http/__init__.py

class HttpResponseUnauthorized(HttpResponse):
    status_code = 401

class HttpResponseCreated(HttpResponse):
    status_code = 201

#-----------------------------------------------------------------------------


def issues_list_popular(request):
    #request.user.is_authenticated()
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    req = urllib2.Request(EMOCRACY_API_SERVER+"issues/?page=%s" %page)
    try:
        response = urllib2.urlopen(req)
    except HTTPError, e:
        if __debug__:
            print 'The server couldn\'t fulfill the request.'
            print 'Error code: ', e.code
    except URLError, e:
        if __debug__:
            print 'We failed to reach the server.'
            print 'Reason: ', e.reason
        return url_error_view(request, e)
    else:
        pass
    data = response.read()
    #print data
    extra_context = json.loads( data )
    #print extra_context
    #if extra_context.has_key('next'):
    #    print 'next: ' + extra_context['next']
    #    next = extra_context['next']
    #    next = next.split('/')[-1:]
    #    extra_context['next'] = next[0]
    #else:
    #    extra_context['next'] = ''
    #if extra_context.has_key('previous'):
    #    print 'previous: ' + extra_context['previous']
    #    previous = extra_context['previous']
    #    previous = previous.split('/')[-1:]
    #    extra_context['previous'] = previous[0]
    #else:
    #    extra_context['previous'] = ''
    #print extra_context
    fetch = []
    for resource in extra_context:
        issueid = resource['issue_uri'].split('/')
        issueid = issueid[-2:]
        issueid = issueid[0]
        resource_data = {}
        resource_data['id'] = issueid
        # FIXME next line deals with microseconds. bad hack, fix with python 2.6
        resource_datetime = datetime.datetime.strptime(resource['time_stamp'],"%Y-%m-%d %H:%M:%S")
        now = datetime.datetime.now()
        dt = now - resource_datetime
        resource_data['title'] = resource['title']
        resource_data['body'] = resource['body']
        resource_data['votes_for'] = resource['votes_for']
        resource_data['votes_abstain'] = resource['votes_abstain']
        resource_data['votes_against'] = resource['votes_against']
        if not dt.days:
            resource_data['age'] = 'Today'
        else:
            resource_data['age'] = '%s days ago' % dt.days
        resource_data['user'] = resource['owner']['username']
        userid = resource['owner']['user_uri'].split('/')
        userid = userid[-2:]
        resource_data['userid'] = userid[0]
        fetch.append(resource_data)
    context = {}
    context['issues'] = fetch
    return render_to_response('issue_list.html', 
            RequestContext(request, context))

def issues_issue_detail(request, pk):
    req = urllib2.Request(settings.EMOCRACY_API_SERVER+"issues/%s/" % pk)
    response = urllib2.urlopen(req)
    issuedata = response.read()
    extra_context = json.loads( issuedata )[0]
    #print extra_context
    #print owner_context
    userid = extra_context['owner']['user_uri'].split('/')
    userid = userid[-2:]
    extra_context['owner']['id'] = userid[0]
    extra_context['id'] = pk
    return render_to_response('issue_detail.html', 
            RequestContext(request, extra_context))


def issues_issue_vote(request, pk):
    req = urllib2.Request(settings.EMOCRACY_API_SERVER+"issues/")
    response = urllib2.urlopen(req)
    data = response.read()
    extra_context = {"issue_data": data}
    return render_to_response('issue_vote.html', 
            RequestContext(request, extra_context))

def issues_list_hottest(request):
    return issues_list_popular(request)

def issues_list_newest(request):
    return issues_list_popular(request)

def user_logout(request):
    return render_to_response('login.html')
def user_login(request):
    return render_to_response('login.html')

def user_details(request, pk):
    req = urllib2.Request(settings.EMOCRACY_API_SERVER+"users/%s/" % pk)
    response = urllib2.urlopen(req)
    issuedata = response.read()
    extra_context = json.loads( issuedata )[0]
    extra_context['userid'] = pk
    return render_to_response('user_detail.html',
            RequestContext(request, extra_context))

def top_level_menu(request):
    return render_to_response('menu.html',
            RequestContext(request, {'is_menu' : True}))

def url_error_view(request, error):
    return render_to_response(
        'url_error_view.html',
        RequestContext(request, {'error' : error})
    )
"""
def ajax_vote(request):
    '''
    function used by the vote bar
    '''
    vote = request.POST['vote']
    issue = request.POST['issue']
    try:
        blank = request.POST['blank']
    except:
        blank = "no reason specified"
    req = urllib2.Request(EMOCRACY_API_SERVER+"votes/?page=%s" %page) 
"""
