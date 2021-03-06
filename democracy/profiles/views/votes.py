# All views todo with votes + profiles.

from voting.models import Vote
from voting.views import vote_on_object
from voting.managers import possible_votes, votes
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models.sql.datastructures import EmptyResultSet
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.db.models.query import QuerySet
from registration.signals import user_activated

from issue.models import Issue
from django.contrib.auth.views import password_reset

from tagging.models import Tag
from tagging.utils import calculate_cloud

from profiles.views import get_user_candidate_context


@login_required
def record_vote_on_user(request, user_id):
    """
    Wrapper function for the voting.views.vote_on_object function.

    -Handle vote on user, check if direction == 1.
    -Handle ajax votes.
    """
    if request.REQUEST.has_key('direction'):
        direction = int(request.REQUEST['direction'])
        if (not request.is_ajax()) and not direction == 1: 
            message = _("You did not pick a valid option")
            request.session["flash_msg"] = message
            next = request.REQUEST.get('next', '/' )
            return HttpResponseRedirect(next) 
        return vote_on_object(request, User, direction, object_id=user_id, allow_xmlhttprequest=True ) 
    return HttpResponseRedirect('/')


def get_tagcloud_intersection(agree_issues, disagree_issues):
    try :
        agree_tags = Tag.objects.usage_for_model(Issue, 
            counts=True, filters=dict(id__in=agree_issues))
    except EmptyResultSet:
        agree_tags = []
    try:
        disagree_tags = Tag.objects.usage_for_model(Issue, 
            counts=True, filters=dict(id__in=disagree_issues))
    except EmptyResultSet:
        disagree_tags = [] 

    tags_dagree= dict((tag.name, tag) for tag in disagree_tags)
    all_tags = []
    # loop over al for tags, look if tag also exists in disagree tag
    # if so add a status with 'conflict' to the tag.
    # agree_tags have 'agree' status
    # disagree_tags have no status.
    for a_tag in agree_tags:
        a_tag.status = 'agree'
        if tags_dagree.has_key(a_tag.name):
            d_tag = tags_dagree[a_tag.name]
            d_tag.count = d_tag.count + a_tag.count
            d_tag.status = 'conflict'
            all_tags.append(d_tag)
            tags_dagree.pop(a_tag.name)
        else:
            all_tags.append(a_tag)

    all_tags.extend(tags_dagree.values())
    
    return calculate_cloud(all_tags)


def compare_votes_to_user(request, username):
    """ Compare ``request.user``'s voting history with ``username``.
        sidebar:
            Collored Tag cloud. Green=Agree, Yellow=Conflict, Red=Disagree.
        gamenews:
            Candidate info.
            user details.
    """
    user = get_object_or_404(User, username = username)
    user_votes = Vote.objects.get_user_votes(user, Model=Issue)

    if request.user.is_authenticated():
        players_votes = Vote.objects.get_user_votes(request.user, Model=Issue)
        vote_keys = players_votes.values_list('object_id')
        players_votedict = dict((vote.object_id, vote.direction) for vote in players_votes.all())
        #players_votedict = players_votes.values('object_id', 'vote')
    else:
        votedict = request.session.get('vote_history', dict())
        players_votedict = dict((i, int(x)) for i, x in votedict.items())
        vote_keys = players_votedict.keys()

    intersection_votes = user_votes.filter(object_id__in=vote_keys)
    intersection_votes = intersection_votes.values_list('object_id','direction')

    # Now compare votes.
    id_agree = [] 
    id_disagree = [] 
    id_blank = []
    for k, vote in intersection_votes:
        if players_votedict.has_key(k): # must always be true..
            # If both vote the same, that is agreement.
            if players_votedict[k] == vote:
                id_agree.append(k) 
            # Both voting blanc is consirdered to be in agreement. 
            elif (players_votedict[k] > 1 and vote > 1):
                id_agree.append(k) 
            # One blanc vote is considered neither agreement nor 
            # disagreement.
            elif (players_votedict[k] > 1 or vote > 1):
                id_blank.append(k)
            # Disagreement:
            else:
                id_disagree.append(k)


    n_agree, n_disagree, n_blank =  len(id_agree) , len(id_disagree) , len(id_blank)
    n_total_intersection = n_agree + n_disagree + n_blank

    # get the issues + votes!
    def _cmp(issueA, issueB): #comapre issues.
        return cmp(issueA[0].title.lower(), issueB[0].title.lower())

    def _issue_vote(qs): #create list with tuples (issue, direction)
        issue_vote = []
        issues = dict((issue.id, issue) for issue in qs.all())
        for id, issue in issues.items():
            vote = players_votedict[id]
            #issue_vote.append((issue, possible_votes[vote]))
            issue_vote.append((issue, votes.get(vote, _('blank'))))
            issue_vote.sort(_cmp)
        return issue_vote

    agree_issues = Issue.objects.filter(id__in=id_agree)
    agree_issues = _issue_vote(agree_issues) 
    disagree_issues = Issue.objects.filter(id__in=id_disagree)
    disagree_issues = _issue_vote(disagree_issues)
    blank_issues = Issue.objects.filter(id__in=id_blank)
    blank_issues = _issue_vote(blank_issues)

    ## Get tagcloud of vote intersection.
    cloud = get_tagcloud_intersection(id_agree, id_disagree)

    def tag_cmp(tagA, tagB):
        return cmp(tagA.name, tagB.name)
    cloud.sort(tag_cmp)
    
    context = RequestContext(request, {
        'user_to_compare' : user,
        'n_agree' : n_agree,
        'n_disagree' : n_disagree,
        'n_blank' : n_blank,
        'n_total_intersection' : n_total_intersection,
        'agree_issues' : agree_issues,
        'disagree_issues' : disagree_issues,
        'blank_issues' : blank_issues,
        'cloud' : cloud,
        })
    context.update(get_user_candidate_context(request, user))
    return render_to_response('profiles/compare_votes_to_user.html', context)
