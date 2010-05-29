'''This views module implements the dutch general elections of june 2010 feature
for derdekamer.net . As time is limited this module is very simple and not meant
to be reused. '''
from django.contrib.auth.models import User
from voting.models import Vote
from django.template import RequestContext
from django.shortcuts import render_to_response

PARTY_USERS = [
    'CDA2010',
    'PvdA2010',
    'SP2010',
    'VVD2010',
    'PVV2010',
    'GroenLinks2010',
    'ChristenUnie2010',
    'D662010',
    'PartijvoordeDieren2010',
    'SGP2010',
    'NieuwNederland2010',
    'TrotsopNederland2010',
    'MENS2010',
    'PartijEen2010',
    'Lijst172010',
    'Piratenpartij2010',
]


def compare_to_parties(request):
    '''Compare ``request.user`` to hardcoded users that represent the parties
    in the june 2010 Dutch general elections.'''
    # TODO : hook this up with some caching!
    party_users = User.objects.filter(username__in = PARTY_USERS)
    # Grab the votes from the database, construct dictionaries keyed by 
    # object_id (of an Issue) and values being an integer that describes the
    # actual vote, (-1, 0, 1) for (against, blanc, for) respectively.
    # First for the player/site visitor:
    if request.user.is_authenticated():
        players_votes = Vote.objects.get_user_votes(request.user)
        players_votedict = dict((vote.object_id, vote.vote) for vote in players_votes.all())
    else:
        votedict = request.session.get('vote_history', dict())
        players_votedict = dict((i, int(x)) for i, x in votedict.items())
    # And then for the party representing users:
    compared = []
    for user in party_users:
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
        # construct a list with tuples with entries :
        # 0 name of party user
        # 1 number of times the player/visitor agrees with this party
        # 2 number of times the player/visitor or party have voted blank
        # 3 number of times the player/visitor disagrees with the party users
        # 4 total number of votes in the intersection between the 
        #   player/visitors vote history and the party 
        compared.append((user.username, n_agree, n_blank, n_disagree, n_agree + n_blank + n_disagree))
        
    context = RequestContext(request, {
        'compared' : compared,
    })
    return render_to_response('juni2010/compare.html', context)