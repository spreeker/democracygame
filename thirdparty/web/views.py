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
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from oauth_consumer.consumer import DemoOAuthConsumerApp
from web.forms import IssueFormNew

demo = DemoOAuthConsumerApp()

#-----------------------------------------------------------------------------
# Some extra response codes not defined in:
# http://code.djangoproject.com/browser/django/tags/releases/1.0.2/django/http/__init__.py

class HttpResponseUnauthorized(HttpResponse):
    status_code = 401

class HttpResponseCreated(HttpResponse):
    status_code = 201

#-----------------------------------------------------------------------------
def index(request):
    """
    returns empty body
    """
    pass

def issues_list_hottest(request):
    
    issue_list = demo.get_issue_list(request)

    fetch = []
    for resource in issue_list:
        issueid = resource['issue_uri'].split('/')
        issueid = issueid[-2:]
        issueid = issueid[0]
        resource_data = {}
        resource_data['id'] = issueid
        resource_datetime = datetime.datetime.strptime(resource['time_stamp'],"%Y-%m-%d %H:%M:%S")
        now = datetime.datetime.now()
        dt = now - resource_datetime
        if request.user.is_anonymous():
            pass
        else:
            if not resource['my_vote'] == []:
                resource_data['my_vote'] = resource['my_vote'][0]['vote']
            else:
                resource_data['my_vote'] = None
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

def issues_list_popular(request):
    return issues_list_hottest(request)

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

def issues_list_newest(request):
    return issues_list_hottest(request)


@login_required
def issues_add_issue(request, issue_no=None):
    """
    This view handles proposing new issues.
    """
    if issue_no is not None: # view was called to edit an issue
        issue = demo.get_issue(request, issue_no)
        #issue = get_object_or_404(Issue, pk = issue_no)
        try:
            # TODO
            # If users were to be allowed to change their opinion on their own
            # issue the following line needs to use a filter() instead of get().
            v = Vote.objects.get(issue = issue, owner = request.user)
            owners_direction = v.direction
        except:
            owners_direction = 1
        if issue.owner != request.user: # check that user is owner
            # TODO add is_draft check
            # TODO add more appropriate Http Response code if user tries to
            # change an issue that is not theirs.
            raise Http404
        # TODO check type of payload in some future where there might be more
        # than just IssueBody objects linked to Issue objects.
        issue_body = issue.payload
        # note the following ties into the IssueFormNew definition in web/forms.py
        data = {
            'title' : issue.payload.title,
            'body' : issue.payload.body,
            'url' : issue.payload.url,
            'source_type' : issue.payload.source_type,
            'owners_vote' : owners_direction,
            'is_draft': issue.is_draft
        }

    if request.method == "POST":
        form = IssueFormNew(request.POST)
        if form.is_valid():
            status = demo.post_issue(
                request,
                {
                    'title' : form.cleaned_data[u'title'],
                    'body' : form.cleaned_data[u'body'],
                    'owners_vote' : form.cleaned_data[u'owners_vote'],
                    'url' : form.cleaned_data[u'url'],
                    'source_type' : form.cleaned_data[u'source_type'],
                    'is_draft' : form.cleaned_data[u'is_draft'],
                    'issue_no' : issue_no,
                }
            )

            #return HttpResponseRedirect(reverse('web_issue_detail', args = [new_issue.pk]))
            if status == 200:
                return HttpResponseRedirect(reverse('top_level_menu'))
            else:
                return HttpResponseRedirect(reverse('issues_submit_error'))
    else:
        if issue_no == None:
            form = IssueFormNew()
        else:
            form = IssueFormNew(data)

    context = RequestContext(request, {"form" : form})
    return render_to_response("new_issue.html", context)
 
def issues_submit_error(request):
    context = RequestContext(request, {})
    return render_to_response("issues_submit_error.html", context)

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
    issue_list = demo.get_issue_list(request)
    fetch = []
    for resource in issue_list:
        issueid = resource['issue_uri'].split('/')
        issueid = issueid[-2:]
        issueid = issueid[0]
        resource_data = {}
        resource_data['id'] = issueid
        resource_datetime = datetime.datetime.strptime(resource['time_stamp'],"%Y-%m-%d %H:%M:%S")
        now = datetime.datetime.now()
        dt = now - resource_datetime
        if request.user.is_anonymous():
            pass
        else:
            voteList = resource.get('my_vote', [] )
            if voteList:
                resource_data['my_vote'] = voteList[0]['vote']
            else:
                resource_data['my_vote'] = None

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
    context['is_menu'] = True
    return render_to_response('interface.html',
            RequestContext(request, context))

def url_error_view(request, error):
    return render_to_response(
        'url_error_view.html',
        RequestContext(request, {'error' : error})
    )
