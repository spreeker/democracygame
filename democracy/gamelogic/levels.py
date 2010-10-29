"""
The game level upgrade functions which are exectuted on a score change 

This module manages the leveling of a user.
From somewhere in the code where an action changes the score,
change the score using the change_score method in the module.
"""

from profiles.models import UserProfile
from voting.models import Vote
from django.contrib.auth.models import User

import logging

# put these values in a database??
MAX_PARLEMENT = 15
MAX_OPINION_LEADERS = 50
MIN_SCORE_ACTIVE_CITIZENS = 30 # onchange edit template/isssue/myissuelist to.

def anonymous_citizen(user, userprofile):
    """No code needed , upgrade is to citizen is done when you are registering an account
    """
    pass
    #return 'anonymous citizen'

def citizen(user, userprofile):
    if userprofile.score >= MIN_SCORE_ACTIVE_CITIZENS:
        userprofile.role = 'active citizen'
        return 'active citizen'
     
def active_citizen(user, userprofile):
    """ here the following can happen to a user:
        -downgraded too citizen
        -upgraded to opinion leader
        -upgraded to opinion leader if there are not enough of them 
    """
    if userprofile.score < MIN_SCORE_ACTIVE_CITIZENS:
        userprofile.role = 'citizen'    
        return 'citizen'
    
    # if there are too little opinion leaders , active cititzens get upgraded 
    count_opinion_leaders = UserProfile.objects.filter(role = 'opinion leader').count()

    if count_opinion_leaders < MAX_OPINION_LEADERS: 
        # there are not enough opinion leaders
        # so you will become one automatically.
        userprofile.role = 'opinion leader'
        return 'opinion leader'
        
    opinion_leaders = UserProfile.objects.filter(role = 'opinion leader').\
            order_by('score')

    lowest_opinion_leader = opinion_leaders[0]   
 
    if userprofile.score > lowest_opinion_leader.score: 
        userprofile.role = 'opinion leader'
        lowest_opinion_leader.role = 'active citizen'
        lowest_opinion_leader.save()
        return 'opinion leader' 
  
def opinion_leader(user, userprofile):
    """ opinion leaders get downgraded if there are too many of them
    """
    count_opinion_leaders = UserProfile.objects.filter(role = 'opinion leader').count() 
    #check if max opion leaders is reached.
    if count_opinion_leaders > MAX_OPINION_LEADERS: 
        opinion_leaders = UserProfile.objects.filter(role = 'opinion leader').\
           order_by('-score')
        for low_ol in opinion_leaders[MAX_PARLEMENT:]:
            low_ol.role = 'active citizen'       
            low_ol.save()

    if userprofile.score < MIN_SCORE_ACTIVE_CITIZENS:
        userprofile.role = 'citizen'    
        return 'citizen'

    #if people have voted on you, you become a candidate.
    votes_on_user = Vote.objects.get_for_object(user).count()
    
    if votes_on_user:
        #logging.debug(votes_on_user)
        #logging.debug(user)
        userprofile.role = 'candidate'
        return 'candidate'
 
def candidate(user, userprofile):
    """if people have voted on you as person you can become candidate.
       if you have no personal votes anymore you should be downgraded.
       if you have more votes than the lowest parliament member you
       come into the parliament and the lowerst parliament member drops out.
    """
    votes_on_user = Vote.objects.get_for_object(user).count()
    if not votes_on_user:
        userprofile.role = 'opinion leader'
        return 'opinion leader'

    #check if you are good enough to be in parliament.    
    count_parliament = UserProfile.objects.filter(role='parliament member').count() 

    if count_parliament < MAX_PARLEMENT:
        # there are not enough opinion leaders
        # so you will become one automatically.
        userprofile.role = 'parliament member'
        return 'parliament member'

    # now check if you have more votes than the lowest parliament member. 
    # in case of draw, more points.
    parliament_members = UserProfile.objects.filter(
        role='parliament member').order_by('score')

    candidate_votes = Vote.objects.get_popular(User, 
            object_ids=parliament_members, reverse=True, min_tv=0)

    lowest_vote_count = candidate_votes[0]

    pm_member_with_votes_ids = set([ p['object_id'] for p in candidate_votes ])
    pm_member_ids = set([ profile.user.pk for profile in parliament_members]) 

    #check the case of parliament members without followers.
    losers = pm_member_ids - pm_member_with_votes_ids
    if losers:
        userprofile.role = 'parliament member'
        for member in parliament_members.filter(user__in=losers):
            member.role = 'opinion_leader'            
            member.save()
        return 'parliament member' 

    # all members have followers then...
    # parliament member with the least followers gets downgraded.
    lowest_parliament_member = parliament_members.get(
        user=lowest_vote_count['object_id'])

    if((votes_on_user > lowest_vote_count['score']) or 
        #if equal check score.
       ((votes_on_user == lowest_vote_count['score']) and 
       (userprofile.score > lowest_parliament_member.score))):
        userprofile.role = 'parliament member'
        #downgrade lowest member
        lowest_parliament_member.role = 'candidate'
        lowest_parliament_member.save()
        return 'parliament member' 
 
def parliament_member(user, userprofile):
    """If you are the top voted candidates, you get into the parliament 
       If you are not anymore you get downgraded. 
       This is done by upcoming candidates.
    """
    votes_on_user = Vote.objects.get_for_object(user).count()
    if not votes_on_user:
        userprofile.role = 'opinion leader'
        return 'opinion leader'


def minister(user, userprofile):
    """You get voted to become minister. minister changes are unknown for now.
    """
    pass

def party_program(user, userprofile):
    """
    this is the special party program profile. for party programs.
    easy entrance of users.
    no changes.
    """
    pass


upgrade = {
    'anonymous citizen' : anonymous_citizen,
    'citizen' : citizen,
    'active citizen' : active_citizen,
    'opinion leader' : opinion_leader,
    'candidate' : candidate,
    'parliament member' : parliament_member,
    'party program' : party_program,
    'minister'  : minister,
    'prime minister' : minister,
}

def change_score(user, score):
    """on score changes check leveling.
    """
    userprofile = user.get_profile()
    userprofile.score += score
    while upgrade[userprofile.role](user, userprofile):
        pass
    userprofile.save()
