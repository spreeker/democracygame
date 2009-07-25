"""
Views for showing and voting on Issues.
"""
import logging
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseServerError
from django.http import Http404, HttpResponseRedirect,HttpResponseBadRequest 
from django.shortcuts import render_to_response, get_object_or_404
from django.template import loader, RequestContext
from django.core.urlresolvers import reverse
from django.views.generic.list_detail import object_list
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from gamelogic import actions
from democracy.issue.models import Issue
from democracy.voting.managers import possible_votes, blank_votes
from democracy.voting.models import Vote
from democracy.voting.views import vote_on_object


def paginate(request, qs):
    paginator = Paginator(qs, 8) #TODO add to settings.py
    try:
        pageno = int(request.GET.get('page', '1'))
    except ValueError:
        pageno = 1
    try:
        page = paginator.page(pageno)
    except (EmptyPage, InvalidPage):
        page = paginator.page(paginator.num_pages) #last page
    return page


def order_issues(request, sortorder, issues):
    """ return page and qs of issues derived from voting data.  """
    if sortorder == 'popular':
        qs = Vote.objects.get_popular(Issue)
    elif sortorder == 'controversial':
        qs = Vote.objects.get_controversial(Issue)
    elif sortorder == 'new': 
        # we dont need voting data for this one.
        #default issues is wat we want
        page = paginate(request, issues)
        return page.object_list, page 
    else:
        return

    page = paginate(request, qs)
    object_ids = [ d['object_id'] for d in page.object_list ]
    issues = issues.filter( id__in=object_ids )

    return issues, page

def issue_list(request, *args, **kwargs):
    """ 
    shows issues to vote on in different sortings
    based on collective knowlegde from votings on them
    """
    template_name= "issue/issue_list.html"

    if not request.method == "GET":
        return HttpResponseBadRequest

    issues = Issue.objects.select_related().order_by('-time_stamp')

    if 'sortorder' in kwargs:
        issues, page = order_issues(request, kwargs['sortorder'], issues)
    else:
        page = paginate(request, issues)
        issues = page.object_list

    c = RequestContext(request, {
        'blank_votes' : blank_votes.items(),
        'possible_votes' : possible_votes,
        'issues'  : issues, 
        'page' : page,
        'votedata' : Vote,
    }) 
   
    t = loader.get_template(template_name)
    return HttpResponse(t.render(c))

def record_vote(request, issue_id ):
    """
    Wrapper function for the voting.views.vote_on_object function

    what if user is anonymous?

    """
    if request.REQUEST.has_key('direction'):
        direction = request.REQUEST['direction']
        return vote_on_object(request, Issue, direction , object_id=issue_id ) 
    return HttpResponseRedirect( '/' )

def record_multiply(request , issue_id ):
    """
    Wrapper funtion around gamelogic.actions.multiply
    """
    if not request.method == "POST": 
        return HttpResponseBadRequest()
    issue = get_object_or_404( Issue, id=issue_id ) 

    possible_actions = actions.get_actions(request.user) 
    message = "You cannot multiply yet!"
    next = request.REQUEST.get('next' , '/' )

    if possible_actions.has_key('multiply') :
        actions.multiply( request.user, issue )
        return HttpResponseRedirect(next)

    request.user.message_set.create(message=message)    
    return HttpResponseRedirect( next )
