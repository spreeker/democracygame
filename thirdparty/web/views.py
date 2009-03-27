# Create your views here.

import urllib2
import datetime
import time

from django.core import serializers
from django.utils import simplejson as json
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template import RequestContext

#-----------------------------------------------------------------------------
# Some extra response codes not defined in:
# http://code.djangoproject.com/browser/django/tags/releases/1.0.2/django/http/__init__.py

class HttpResponseUnauthorized(HttpResponse):
    status_code = 401

class HttpResponseCreated(HttpResponse):
    status_code = 201

#-----------------------------------------------------------------------------
EMOCRACY_API_SERVER = "http://emo.buhrer.net:8080/api/"


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
    else:
        pass
    data = response.read()
    print data
    extra_context = json.loads( data )
    print extra_context
    if extra_context.has_key('next'):
        print 'next: ' + extra_context['next']
        next = extra_context['next']
        next = next.split('/')[-1:]
        extra_context['next'] = next[0]
    else:
        extra_context['next'] = ''
    if extra_context.has_key('previous'):
        print 'previous: ' + extra_context['previous']
        previous = extra_context['previous']
        previous = previous.split('/')[-1:]
        extra_context['previous'] = previous[0]
    else:
        extra_context['previous'] = ''
    print extra_context
    fetch = []
    for resource in extra_context['resources']:
        issueid = resource.split('/')
        issueid = issueid[-2:]
        issueid = issueid[0]
        req = urllib2.Request(resource)
        response = urllib2.urlopen(req)
        data = response.read()
        resource_data = json.loads( data )
        resource_data['id'] = issueid
        # FIXME next line deals with microseconds. bad hack, fix with python 2.6
        resource_datetime = datetime.datetime(*time.strptime(
            resource_data['time_stamp'].split('.')[0],'%Y-%m-%d %H:%M:%S')[:6])
        now = datetime.datetime.now()
        dt = now - resource_datetime
        if not dt.days:
            resource_data['age'] = 'Today'
        else:
            resource_data['age'] = '%s days ago' % dt.days
        req = urllib2.Request(resource_data['owner'])
        response = urllib2.urlopen(req)
        data = response.read()
        resource_data['user'] = json.loads( data )
        userid = resource_data['owner'].split('/')
        userid = userid[-2:]
        resource_data['userid'] = userid[0]
        fetch.append(resource_data)
    extra_context['issues'] = fetch
    return render_to_response('issue_list.html', 
            RequestContext(request, extra_context))

def issues_issue_detail(request, pk):
    req = urllib2.Request(EMOCRACY_API_SERVER+"issues/%s/" % pk)
    response = urllib2.urlopen(req)
    issuedata = response.read()
    extra_context = json.loads( issuedata )
    req = urllib2.Request(extra_context['owner'])
    response = urllib2.urlopen(req)
    ownerdata = response.read()
    owner_context = json.loads( ownerdata )
    #print extra_context
    #print owner_context
    extra_context['user'] = owner_context
    userid = extra_context['owner'].split('/')
    userid = userid[-2:]
    extra_context['user']['id'] = userid[0]
    return render_to_response('issue_detail.html', 
            RequestContext(request, extra_context))


def issues_issue_vote(request, pk):
    req = urllib2.Request(EMOCRACY_API_SERVER+"issues/")
    response = urllib2.urlopen(req)
    data = response.read()
    extra_context = {"issue_data": data}
    return render_to_response('issue_vote.html', 
            RequestContext(request, extra_context))

def issues_list_hottest(request):
    return issues_list_popular(request)

def issues_list_newest(request):
    return issues_list_popular(request)

def user_login(request):
    return render_to_response('login.html')

def user_details(request, pk):
    req = urllib2.Request(EMOCRACY_API_SERVER+"users/%s/" % pk)
    response = urllib2.urlopen(req)
    issuedata = response.read()
    extra_context = json.loads( issuedata )
    extra_context['userid'] = pk
    return render_to_response('user_detail.html',
            RequestContext(request, extra_context))

def top_level_menu(request):
    return render_to_response('menu.html',
            RequestContext(request, {'is_menu' : True}))
