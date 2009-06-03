# The game level upgrade functions which are exectuted on score change 

NUMBER_OF_OPINION_LEADERS = 10
MIN_SCORE_ACTIVE_CITIZENS = 50

def anonymous_citizen(user):
    """No code needed , upgrade is to citizen is done when you are registering an account
    """
    return 'anonymous citizen'

def citizen(userprofile):
    if user.userprofile.score > MIN_SCORE_ACTIVE_CITIZENS:
        userprofile.role = 'active citizen'
        userprofile.save()
        return 'active citizen'
    else:
        return 'citizen'
        
def active_citizen(userprofile):
    opinion_leaders = UserProfile.objects.filter(role = 'opinion leader').sort_by(-score)[:NUMBER_OF_OPINION_LEADERS]
    if userprofile.score > opinion_leaders[-1].score:
        userprofile.role = 'opinion leader'
        userprofile.save()
        to_be_downgraded = opinion_leaders[-1]
        to_be_downgraded.role = 'active citizen'
        to_be_downgraded.save()
        return 'opinion leader'
    else :
        return 'active citizen'

def opinion_leader(user):
    pass

upgrade = {
    'anonymous citizen' : anonymous_citizen,
    'citizen' : citizen,
    'active citizen' : active_citizen,
    'opinion leader' : opinion_leader
}

def update_level(sender , **kwargs):
    """ a handler for a save on UserProfile """
    upgrade[sender.role](sender)
