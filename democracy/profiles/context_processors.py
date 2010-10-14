from profiles.models import UserProfile
import logging

def userprofile(request):
    """
    This context processor adds the userprofile to the context of the
    template engine if a user is logged in.
    
    In case of a anonymous user, default values get loaded. 
    """
    if request.user.is_authenticated():
        try:
            profile = request.user.get_profile()
        except UserProfile.DoesNotExist: 
            profile = UserProfile.objects.create(user=request.user, score=0, role='citizen')

        return {'userprofile' : profile }
    else:
        defaults = { 'score' : 0, 'role' : 'anonymous citizen' }
        return {'userprofile' : defaults }
