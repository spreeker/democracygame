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

from django.utils import simplejson as json

from oauth_consumer.consumer import DemoOAuthConsumerApp
from forms import VoteForm

from utils import index_conversion

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
        retstatus = demo.post_vote(request, form.clean())
    else:
        pass #for now

    if retstatus != 201:
        error = "vote cast failed, code %d" % retstatus
        status = simplejson.dumps({'status': 'debug', 'error': error})
        return http.HttpResponseServerError(status, mimetype="application/json")

    # Save the vote and signal that it was saved
    status = simplejson.dumps({'status': "success"})
    return http.HttpResponse(status, mimetype="application/json")


def ajax_get_issues_list_ordered( request, sortorder, page=1 ):
    """
    Return sorted by `sortorder` issues list
    """
    # get issue URI
    # lookup issue votecount from cache
    # return json
    error = ""

    local_paginate = 5
    remote_paginate = 25
    try:
        page = int(page)
    except:
        pass

    (remote_start, remote_end ) = index_conversion(page, local_paginate, remote_paginate)

    remote_pages = []
    get = remote_start[0]+1
    while get <= (remote_end[0]+1):
        response = demo.get_issues_list_ordered(request, sortorder, get)
        page = json.loads(response.read())
        if remote_start[0] == remote_end[0]:
            remote_pages.extend(page[remote_start[1]:remote_end[1]+1])
        elif get == remote_start[0]+1:
            remote_pages.extend(page[remote_start[1]:])
        elif get == remote_end[0]+1:
            remote_pages.extend(page[:remote_end[1]+1])
        else:
            remote_pages.extend(page)
        get += 1

    print remote_pages
    # Otherwise submit the vote to Service Provider

    if response.status != 200:
        error = "getting issue list failed, code %d, reason %s" % (response.status, response.reason)
        status = simplejson.dumps({'status': 'debug', 'error': error})
        return http.HttpResponseServerError(status, mimetype="application/json")

    # Save the vote and signal that it was saved
    status = json.dumps(remote_pages)
    return http.HttpResponse(status, mimetype="application/json")
