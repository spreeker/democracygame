# Create your views here.

import datetime
import time


from urllib2 import HTTPError, URLError
from django.conf import settings
from django.core import serializers
from django.utils import simplejson as json
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.views.decorators.cache import cache_page
from django.views.decorators.cache import cache_control
from django.views.decorators.vary import vary_on_headers

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

@cache_control(public=True)
@cache_page(60 * 60 * 24 * 15)
def issue_ajax(request, issueid):

    issue = demo.get_issue(request, issueid)
    if issue == []:
        # TODO: handle this better, possibly with more status codes
        return HttpResponseNotFound()
    issue['id'] = issueid
    return render_to_response('issue.html', 
        RequestContext(request, {'issue' : issue}))

@cache_control(private=True)
@vary_on_headers('User-Agent', 'Cookie')
@cache_page(0)
def myvote_ajax(request, issueid):

    vote = demo.get_issue_vote(request, issueid)
    if vote == []:
        vote = {}
        vote['vote'] = None
        vote['issueid'] = issueid
        vote['keep_private'] = False
    if type(vote) == type(list()):
        vote = vote[-1]
    vote['issueid'] = issueid
    return render_to_response('voteform.html',
        RequestContext(request, {'vote' : vote}))

@cache_page(0)
def vote_totals_ajax(request, issueid):

    votes = demo.get_issue_votes(request, issueid)
    print votes
    totals = {}
    if votes == []:
        totals['votes_for'] = 0
        totals['votes_against'] = 0
        totals['votes_abstain'] = 0
    else:
        votes.pop(u'0', None)
        totals['votes_for'] = votes.pop(u'1', 0)
        totals['votes_against'] = votes.pop(u'-1', 0)
        totals['votes_abstain'] = sum([v for v in votes.values()])
    totals['issueid'] = issueid
    print totals
    return render_to_response('votetotals.html',
        RequestContext(request, {'totals' : totals } ))

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
                    # TODO : fix naming owners_vote/direction
                    'direction' : form.cleaned_data[u'owners_vote'],
                    'url' : form.cleaned_data[u'url'],
                    'source_type' : form.cleaned_data[u'source_type'],
                    'is_draft' : form.cleaned_data[u'is_draft'],
                    'issue_no' : issue_no,
                }
            )
            print 'STATUS', status
            
            #return HttpResponseRedirect(reverse('web_issue_detail', args = [new_issue.pk]))
            if status == 201:
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

@login_required
def interface(request):
    context = {}
    context['is_menu'] = True
    return render_to_response('interface.html',
            RequestContext(request, context))


def debug(request):
    vote = demo.get_issue_vote(request, 1)
    context = {'json' : vote}
    return render_to_response('debug.html',
            RequestContext(request, context))


def url_error_view(request, error):
    return render_to_response(
        'url_error_view.html',
        RequestContext(request, {'error' : error})
    )
