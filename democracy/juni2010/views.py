'''This views module implements the dutch general elections of june 2010 feature
for derdekamer.net . As time is limited this module is very simple and not meant
to be reused. '''

from django.contrib.auth.models import User
from profiles.models import UserProfile
from issue.models import Issue
from voting.models import Vote
from django.template import RequestContext
from django.shortcuts import render_to_response
import logging

def compare_to_parties(request):
    '''Compare ``request.user`` to hardcoded users that represent the parties
    in the june 2010 Dutch general elections.
    '''
    # TODO : hook this up with some caching!
    party_users = UserProfile.objects.filter(role = 'party program')
    # Grab the votes from the database, construct dictionaries keyed by 
    # object_id (of an Issue) and values being an integer that describes the
    # actual vote, (-1, 0, 1) for (against, blanc, for) respectively.
    # First for the player/site visitor:
    if request.user.is_authenticated():
        user_votes = Vote.objects.get_user_votes(request.user)
        user_votedict = dict((vote.object_id, vote.direction) for vote in user_votes.all())
    else:
        votedict = request.session.get('vote_history', dict())
        user_votedict = dict((issue_id, int(direction)) for issue_id, direction in votedict.items())
    # And then for the party representing users:

    compared = []
    for party in party_users:
        party_votes = Vote.objects.get_user_votes(party.user, Model=Issue)
        party_votedict = dict((vote.object_id, vote.direction) for vote in party_votes.all())
                
        # Now compare the two dictionaries of votes and construct a tuple with 
        n_agree = 0
        n_disagree = 0
        n_blank = 0
        for k, direction in party_votedict.items():
            if user_votedict.has_key(k):
                # party issues are always for=1.
                if user_votedict[k] == 1:
                    n_agree += 1
                # One blanc vote
                elif (user_votedict[k] > 1 ):
                    n_blank += 1
                # Disagreement
                else:
                    n_disagree += 1

        # construct a list with tuples with entries :
        #  agree / disagree
        #  name of party user
        #  number of times the player/visitor agrees with this party
        #  number of times the player/visitor or party have voted blank
        #  number of times the player/visitor disagrees with the party users
        #  total number of votes in the intersection between the 
        #   player/visitors vote history and the party 
        all_votes = n_agree + n_blank + n_disagree
        agreeing = 0.0
        if all_votes and n_agree:
            agreeing = float(n_agree) / all_votes * 100.0

        compared.append((agreeing, party.user.username, n_agree, n_blank, n_disagree, n_agree + n_blank + n_disagree))
        
    compared.sort(reverse=True)
    context = RequestContext(request, {
        'compared' : compared,
        'current' : 'juni_2010',
    })
    return render_to_response('juni2010/compare.html', context)
