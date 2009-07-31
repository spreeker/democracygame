"""
The game level upgrade functions which are exectuted on a score change 

This module manages the leveling of a user.
From somewhere in the code where an action changes the score,
change the score using the change_score method in the module.
"""

from profiles.models import UserProfile

# put these values in a database??
MAX_OPINION_LEADERS = 5
MIN_SCORE_ACTIVE_CITIZENS = 10

def anonymous_citizen(userprofile):
    """No code needed , upgrade is to citizen is done when you are registering an account
    """
    return 'anonymous citizen'

def citizen(userprofile):
    if userprofile.score >= MIN_SCORE_ACTIVE_CITIZENS:
        userprofile.role = 'active citizen'
        return 'active citizen'
     
def active_citizen(userprofile):
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

  
def opinion_leader(userprofile):
    """ opinion leaders get downgraded if there are too many of them
    """
    count_opinion_leaders = UserProfile.objects.filter(role = 'opinion leader').count() 
    
    if count_opinion_leaders > MAX_OPINION_LEADERS: 
        opinion_leaders = UserProfile.objects.filter(role = 'opinion leader').\
           order_by('-score')
        for ol in opinion_leaders[MAX_OPINION_LEADERS:]:
            ol.role = 'active citizen'       
            ol.save()

    if userprofile.score < MIN_SCORE_ACTIVE_CITIZENS:
        userprofile.role = 'citizen'    
        return 'citizen'
 
upgrade = {
    'anonymous citizen' : anonymous_citizen,
    'citizen' : citizen,
    'active citizen' : active_citizen,
    'opinion leader' : opinion_leader
}

def change_score(userprofile, score):
    """ if the score changes, the level might change too """
    userprofile.score += score
    while upgrade[userprofile.role](userprofile): 
        #does the level update checks
        #keep updating until there is no change
        pass
    userprofile.save()

