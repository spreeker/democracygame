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
from django.contrib import comments
from django.contrib.comments import signals
from django.contrib.auth.decorators import login_required

from oauth_consumer import EmoOAuthConsumerApp
from forms import VoteForm

emo = EmoOAuthConsumerApp()

def ajax_vote_cast(request, next=None, xhr="WTF?"):
    """
    Cast a vote

    HTTP POST is required.
    """
    # Fill out some initial data fields from an authenticated user, if present

    if request.user.is_anonymous():
        error = "Must be logged in."
        status = simplejson.dumps({'status' : 'error', 'error' : error})
        return http.HttpResponse(status, mimetype="application/json")
    else:
        if not request.user.get_profile().access_token:
            error = "Must have access token."
            status = simplejson.dumps({'status' : 'error', 'error' : error})
            return http.HttpResponse(status, mimetype="application/json")

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
        response = emo.post_vote(request, form.clean())
    else:
        pass #for now

    #print response.read()
    if response.status != 200:
        error = "vote cast failed, code %d, reason %s" % (response.status, response.reason)
        status = simplejson.dumps({'status': 'debug', 'error': error})
        return http.HttpResponseServerError(status, mimetype="application/json")

    # Save the comment and signal that it was saved
    status = simplejson.dumps({'status': "success"})
    return http.HttpResponse(status, mimetype="application/json")


