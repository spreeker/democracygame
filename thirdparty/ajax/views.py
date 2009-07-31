from django import http
from django.utils import simplejson
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.html import escape
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from oauth_consumer.consumer import DemoOAuthConsumerApp
from forms import VoteForm

demo = DemoOAuthConsumerApp()


def ajax_error(error, status ):
    status = simplejson.dumps({'status' : status, 'error' : error})
    return http.HttpResponse(status, mimetype="application/json")


def ajax_vote_cast(request, next=None, xhr="WTF?"):
    """
    Cast a vote

    HTTP POST is required.
    """
    # Fill out some initial data fields from an authenticated user, if present

    error = ""
    if request.user.is_anonymous():
        return ajax_error( "Must be logged in." , "error" )

    if not request.user.get_profile().access_token:
        error = "Must have access token."
        return ajax_error( error , "error" )

    data = request.POST.copy()

    # Look up the object we're trying vote on
    issue = data.get("issue")
    if issue is None:
        error = "Missing issue field." 
        status = simplejson.dumps({'status': 'debug', 'error': error})
        return http.HttpResponseServerError(status, mimetype="application/json")

    # Construct the vote form
    form = VoteForm(data)

    # If there are errors report
    if form.errors:
        error = ""
        for e in form.errors:
            error += "Error in the %s field: %s" % (e, form.errors[e])
        status = simplejson.dumps({'status' : 'error', 'error' : error })
        return http.HttpResponse(status, mimetype="application/json")
    
    # Otherwise submit the vote to Service Provider
    if form.is_valid():
        print form.cleaned_data
        retstatus = demo.post_vote(request, form.clean())
    else:
        pass #for now

    #print response.read()
    print retstatus
    if retstatus != 201:
        error = "vote cast failed, code %d, reason %s" % (response.status, response.reason)
        status = simplejson.dumps({'status': 'debug', 'error': error})
        return http.HttpResponseServerError(status, mimetype="application/json")

    # Save the vote and signal that it was saved
    status = simplejson.dumps({'status': "success"})
    return http.HttpResponse(status, mimetype="application/json")

def ajax_get_issue( request, issueid ):
    """
    Return issue in json
    """
    # get issue URI
    # loopup issue from cache
    # return the json
    error = ""
    
    response = demo.get_issue_json(request, issueid)
    # Otherwise submit the vote to Service Provider

    #print response.read()
    if response.status != 200:
        error = "getting issue failed, code %d, reason %s" % (response.status, response.reason)
        status = simplejson.dumps({'status': 'debug', 'error': error})
        return http.HttpResponseServerError(status, mimetype="application/json")

    # Save the vote and signal that it was saved
    status = simplejson.dumps({'status': response.read()})
    return http.HttpResponse(status, mimetype="application/json")

def ajax_get_issue_score( request ):
    """
    Return vote counts for issue
    """
    # get issue URI
    # lookup issue votecount from cache
    # return json

def ajax_get_issue_vote( request ):
    """
    return vote for an user
    """
    pass

