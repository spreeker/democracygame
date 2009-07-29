"""
Views for showing / managaging players OWN data. 

# data on your issues 
# your votes
# Show which 3d party has acces acces to them.
"""

import logging
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseServerError
from django.http import Http404, HttpResponseRedirect,HttpResponseBadRequest 
from django.shortcuts import render_to_response, get_object_or_404
from django.template import loader, RequestContext
from django.core.urlresolvers import reverse
from django.views.generic.list_detail import object_list
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from gamelogic import actions
from issue.models import Issue
from issue.views import propose_issue
from voting.managers import possible_votes, blank_votes
from voting.models import Vote
from voting.views import vote_on_object


def paginate(request, qs, ipp=9):
    paginator = Paginator(qs, ipp) #TODO add to settings.py
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
    """ return page and issues derived by voting data.  """
    ids = issues.values_list("id")
    if sortorder == 'popular':
        qs = Vote.objects.get_popular(Issue, ids)
    elif sortorder == 'controversial':
        qs = Vote.objects.get_controversial(Issue, ids)
    elif sortorder == 'all':
        issues = Issue.objects.all() 
        page = paginate(request, issues)
        return page.object_list, page
    else:
        page = paginate(request, issues)
        return page.object_list, page

    page = paginate(request, qs)
    object_ids = [ d['object_id'] for d in page.object_list ]
    issues = issues.filter( id__in=object_ids )

    return issues, page

@login_required
def my_issue_list(request, *args, **kwargs):
    """ 
    shows issues to vote on in different sortings
    based on collective knowlegde from votings on them
    shows issue from to propose issue, if you have the game rights
    """
    template_name= "dashboard/my_issues.html"

    issueform = propose_issue(request)
    issues = Issue.objects.select_related().order_by('-time_stamp')
    issues = issues.filter( user=request.user ) 

    if 'sortorder' in kwargs:
        issues, page = order_issues(request, kwargs['sortorder'], issues)
    else:
        page = paginate(request, issues)
        issues = page.object_list

    c = RequestContext(request, {
        'issueform' : issueform,
        'blank_votes' : blank_votes.items(),
        'possible_votes' : possible_votes,
        'issues'  : issues, 
        'page' : page,
        'actions' : actions.get_actions(request.user),
    }) 

    t = loader.get_template(template_name)
    return HttpResponse(t.render(c))


def order_votes(request, sortorder, votes):
    """ update issues qs acording to qs """
    if sortorder == 'name':
        return votes.order_by('object__title')
    elif sortorder == 'new':
        return votes
    else:
        return votes

@login_required
def my_votes_list(request, *args, **kwargs):
    """
    Show user votes
    """
    template_name = "dashboard/my_votes.html"

    if not request.method == "GET":
        return HttpResponseBadRequest

    myvotes = Vote.objects.get_user_votes(request.user)
    myvotes = myvotes.select_related()
    
    if 'sortorder' in kwargs:
        myvotes = order_issues(request, kwargs['sortorder'], myvotes)
        
    page = paginate(request, myvotes, 50)

    c = RequestContext(request, {
        'blank_votes' : blank_votes.items(),
        'possible_votes' : possible_votes,
        'vote' : Vote,
        'page' : page,
        'my_votes' : page.object_list
    }) 
    t = loader.get_template(template_name)
    return HttpResponse(t.render(c))


@login_required
def archive_vote(request, vote_id ):
    """
    voting.views.vote_on_object function
    """
    if request.method != "POST":
        return HttpResponseBadRequest
    
    vote = get_object_or_404( Vote, id=vote_id, user=request.user)
    
    vote.is_archived = True
    vote.save()
    profile = user.get_profile()
    profile.score = profile.score - 1

    next = request.REQUEST.get('next', '/' )
    return HttpResponseRedirect(next) 

@login_required
def delete_multiply(request , multiply_id ):
    """
    Delete a multiply 
    """
    if not request.method == "POST": 
        return HttpResponseBadRequest()
    m = get_object_or_404(Multiply, id=multiply_id, user=request.user ) 
    m.delete()
    next = request.REQUEST.get('next', '/' )
    message = "multiply deleted"
    request.user.message_set.create(message=message)    
    return HttpResponseRedirect(next)
