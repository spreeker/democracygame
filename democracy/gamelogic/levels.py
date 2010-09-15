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
MIN_SCORE_ACTIVE_CITIZENS = 30

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
    """
    votes_on_user = Vote.objects.get_for_object(user).count()
    if not votes_on_user:
        userprofile.role = 'opinion leader'
        return 'opinion leader'

    #check if you are good enough to be in parlement.    
    count_parlement = UserProfile.objects.filter(role='parlement member').count() 

    if count_parlement < MAX_PARLEMENT:
        # there are not enough opinion leaders
        # so you will become one automatically.
        userprofile.role = 'parlement member'
        return 'parlement member'

    # now check if you have more votes than the lowest parlement member. 
    parlement_members_ids = UserProfile.objects.filter(
        role='parlement member').values_list('id') 
    pm_votes = Vote.objects.get_popular(User, 
            object_ids=parlement_members_ids, reverse=True)

    lowest_vote_count = pm_votes[0]

    lowest_parlement_member = User.objects.get(
        id=lowest_vote_count['object_id']).get_profile()

    if votes_on_user > lowest_vote_count['score']: 
        userprofile.role = 'parlement member'
        #downgrade lowest member
        lowest_parlement_member.role = 'candidate'
        lowest_parlement_member.save()
        return 'parlement member' 
 
def parlement_member(user, userprofile):
    """If you are the top voted candidates, you get into the parlement 
       If you are not anymore you get downgraded. 
       This is done by upcoming candidates.
    """
    pass

upgrade = {
    'anonymous citizen' : anonymous_citizen,
    'citizen' : citizen,
    'active citizen' : active_citizen,
    'opinion leader' : opinion_leader,
    'candidate' : candidate,
    'parlement member' : parlement_member,
}

def change_score(user, score):
    """on score changes check leveling.
    """
    userprofile = user.get_profile()
    userprofile.score += score
    while upgrade[userprofile.role](user, userprofile):
        pass
    userprofile.save()
