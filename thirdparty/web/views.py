# Create your views here.

import urllib2

from django.core import serializers
from django.utils import simplejson
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template import RequestContext

# ------------------------------------------------------------------------------
# Some extra response codes not defined in:
# http://code.djangoproject.com/browser/django/tags/releases/1.0.2/django/http/__init__.py

class HttpResponseUnauthorized(HttpResponse):
    status_code = 401

class HttpResponseCreated(HttpResponse):
    status_code = 201

# ------------------------------------------------------------------------------

# ^api/ ^issues/(?P<pk>\d+)/$
# ^api/ ^votes/$
# ^api/ ^votes/(?P<pk>\d+)/$
# ^api/ ^users/$
# ^api/ ^users/(?P<pk>\d+)/$

def issues_list_popular(request):
    req = urllib2.Request("http://emo.preeker.net/api/issues/")
    response = urllib2.urlopen(req)
    data = response.read()
    extra_context = {"issue_data": data}
    
    return render_to_response('issue_list.html', 
            RequestContext(request, extra_context))

def issues_issue_detail(request, pk):
    req = urllib2.Request("http://emo.preeker.net/api/issues/%s" % pk)
    response = urllib2.urlopen(req)
    data = response.read()
    extra_context = {"issue_data": data}
    return render_to_response('issue_detail.html', 
            RequestContext(request, extra_context))


def issues_issue_vote(request, pk):
    req = urllib2.Request("http://emo.preeker.net/api/issues/")
    response = urllib2.urlopen(req)
    data = response.read()
    extra_context = {"issue_data": data}
    return render_to_response('issue_vote.html', 
            RequestContext(request, extra_context))
