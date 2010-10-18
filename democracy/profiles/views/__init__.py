import copy

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models.sql.datastructures import EmptyResultSet
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseServerError
from django.utils import simplejson
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from gamelogic.models import roles 
from profiles.forms import ChangeProfile
from profiles.models import UserProfile
from voting.models import Vote
from issue.models import Issue
from tagging.models import Tag
from tagging.utils import calculate_cloud


# Imports for activate view

import logging

def get_user_tag_cloud(user):
    votes = Vote.objects.get_user_votes(user, Model=Issue)
    votes = votes.values_list('object_id') 
    try :
        tags = Tag.objects.usage_for_model(Issue, 
            counts=True, filters=dict(id__in=votes))
    except EmptyResultSet:
        tags = []

    return calculate_cloud(tags)


def get_user_candidate_context(request, user,):
    """
    return context with:
    candidate : candidate of user
    followers : users who made user their candidate.(followers)
    """
    context = {}
    #who did this user vote on? 
    candidate = Vote.objects.get_user_votes(user, Model=User)
    if len(candidate):
        candidate = candidate[0]
        candidate = User.objects.get(id=candidate.object_id)
        context.update({'candidate': candidate })
    #who voted on you? 
    followers = Vote.objects.get_for_object(user)
    followers = followers.filter(is_archived=False)
    if len(followers):
        context.update({'followers': followers })
    return context

def userprofile_show(request, username):
    user = get_object_or_404(User, username=username) 
    context = {'viewed_user' : user}

    context.update(get_user_candidate_context(request,user))

    if user == request.user and request.user.is_authenticated:
        form = ChangeProfile(instance=user.get_profile())
        context.update({'form' : form, 'personal' : True })

    context.update({'tags' : get_user_tag_cloud(user),
        'issuecount' : Issue.objects.filter(user=user.id, is_draft=False).count(), 
    })
    context = RequestContext(request, context)
    return render_to_response('profiles/user_detail.html', context)


def search_user(request):
    username = request.GET.get('searchbox', "")
    users = User.objects.filter(username__icontains=username)
    #logging.debug(issues)
    return ranking(request, users) 

def json_error_response(error_message):
    return HttpResponse(simplejson.dumps(dict(success=False,
                    error_message=error_message)))


def xhr_search_user(request,):
    """
    Search view for js autocomplete.

    'user' - string of at least 2 characters or none.
    """
    if request.method != 'GET':
        return json_error_response(
        'XMLHttpRequest search issues can only be made using GET.')

    name = request.GET.get('term', '')

    results = [] 
    if len(name) > 2:
        users_result = User.objects.filter(username__icontains=name) 
        results = [ u.username for u in users_result[:100]]
        
    return HttpResponse(simplejson.dumps(results), mimetype='application/json') 

@login_required
def change_description(request):
    p = request.user.get_profile()
    if request.method == 'POST':
        form = ChangeProfile(request.POST)
        if form.is_valid():
            p.title = form.cleaned_data['title']
            p.description = form.cleaned_data['description']
            p.url = form.cleaned_data['url']
            p.votes_public = form.cleaned_data['votes_public']
            p.show_identity = form.cleaned_data['show_identity']
            p.save()
            return HttpResponseRedirect(reverse('userprofile', args = [request.user.username]))
    else:
        form = ChangeProfile(instance = p)
    context = RequestContext(request, {
        'form' : form,        
    })
    return render_to_response('profiles/user_detail.html', context)


def make_pyramid(parliament):
    """
    return list with pyramid rows.
    1
    2 3
    4 5 6
    7 8 9 10
    11 12 13 14 15
    ...
    """
    rows = []
    row = [] 
    level = 1
    max_index = 1
    for x, profile in enumerate(parliament):
        if x == max_index:
            rows.append(copy.deepcopy(row))
            row = []
            level += 1
            max_index = max_index + level
        row.append(profile)
    # deal with remaining parlement members.
    if row:
        rows.append(row) 
    return rows

def ranking(request, qs=None):
    """Display a list of players ordered by rank""" 
    if not qs:
        users = UserProfile.objects.all().order_by('-score')
    else:
        users = UserProfile.objects.filter(user__in=qs.values_list('id'))

    human_roles = roles.copy()
    human_roles.pop('party program')

    parliament = users.filter(role="parliament member")
    parliament = make_pyramid(parliament)
    ministers = users.filter(role="minister")
    party_programs = users.filter(role="party program")

    users = users.filter(role__in=human_roles.keys())
    users = users.select_related()
    #logging.debug(ranks)
    paginator = Paginator(users, 50) 
    pageno = int(request.GET.get('page','1'))
   
    try:
        page = paginator.page(pageno)
    except(EmptyPage, InvalidPage):
        page = paginator.page(paginator.num_pages)

    party_program = []


    for i, profile in enumerate(page.object_list):
        if qs:
            profile.rank = profile.ranking
        else:
            profile.rank =  (pageno - 1) * 50 + i + 1

    context = RequestContext(request, {'page' : page, 
               'party_programs' : party_programs,
               'parliament' : parliament,
               'ministers' : ministers,
                })
    return render_to_response('profiles/ranking.html', context)
