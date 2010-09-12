# All views todo with votes + profiles.

from voting.models import Vote
from voting.views import vote_on_object
from gamelogic import actions
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from registration.signals import user_activated

from gamelogic import actions
from issue.models import Issue
from django.contrib.auth.views import password_reset

def migrate_votes(request, user, votes):
    """When an User registers, migrate the 
       users session votes to REAL votes.
    """
    for issue_id, direction in votes.items():
        try:
            issue = Issue.objects.get(id=issue_id)
        except Issue.DoesNotExist:
            continue
        actions.vote(user, issue, int(direction), keep_private=False)   


def activate_user(sender, *args, **kwargs):
    """ if user has anoymous votes migrate his votes
        into the database. 
    """ 
    user = kwargs.get('user')
    request = kwargs.get('request')
    if request.session.has_key("vote_history"):
        if user: 
            migrate_votes(request, user, request.session["vote_history"])
            del request.session["vote_history"]

user_activated.connect(activate_user)

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

def compare_to_user(request, username):
    """
    Compare username with request.user.

    Tag cloud match.
    Votes count match.
    Details on differences.

    """
    pass


def compare_votes_to_user(request, username):
    '''Compare ``request.user``'s voting history with ``username``.'''
    user = get_object_or_404(User, username = username)
    # Grab the votes from the database, construct dictionaries keyed by 
    # object_id (of an Issue) and values being an integer that describes the
    # actual vote, (-1, 0, 1) for (against, blanc, for) respectively.
    if request.user.is_authenticated():
        players_votes = Vote.objects.get_user_votes(request.user)
        players_votedict = dict((vote.object_id, vote.vote) for vote in players_votes.all())
    else:
        votedict = request.session.get('vote_history', dict())
        players_votedict = dict((i, int(x)) for i, x in votedict.items())
    users_votes = Vote.objects.get_user_votes(user)
    users_votedict = dict((vote.object_id, vote.vote) for vote in users_votes.all())
    # Now compare the two dictionaries of votes and construct a tuple with 
    n_agree = 0
    n_disagree = 0
    n_blank = 0
    for k, vote in players_votedict.items():
        if users_votedict.has_key(k):
            # If both vote the same, that is agreement.
            if users_votedict[k] == vote:
                n_agree += 1
            # Both voting blanc (even if for different reasons) is consirdered
            # to be in agreement. Assuming blanc votes have integers larger than
            # unity!
            elif (users_votedict[k] > 1 and vote > 1):
                n_agree += 1
            # One blanc vote and one other is considered neither agreement nor 
            # disagreement.
            elif (users_votedict[k] > 1 or vote > 1):
                n_blank += 1
            # Disagreement:
            else:
                n_disagree += 1
    n_total_intersection = n_agree + n_disagree + n_blank

    context = RequestContext(request, {
        'user_to_compare' : user,
        'n_votes_user' : len(users_votedict) - n_total_intersection,
        'n_votes_player' : len(players_votedict) - n_total_intersection,
        'n_agree' : n_agree,
        'n_disagree' : n_disagree,
        'n_blank' : n_blank,
        'n_total_intersection' : n_total_intersection,
    })
    return render_to_response('profiles/compare_votes_to_user.html', context)

