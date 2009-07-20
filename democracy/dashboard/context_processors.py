from democracy.profiles.models import UserProfile

def get_a_profile(request):
    """
    This context processor adds a user's userprofile to the context of the
    template engine if a user is logged in."""
    # This context processor is used by the RequestContext, see the settings.py
    # TEMPLATE_CONTEXT_PROCESSORS variable for the other context processors.
    if request.user.is_authenticated():
        try:
            profile = request.user.get_profile()
        except UserProfile.DoesNotExist: 
            profile = UserProfile.objects.create( user=request.user, score=0, role='citizen' )
        return {'userprofile' : profile }
    else:
        defaults = { 'score' : 0, 'role' : 'anonymous citizen' }
        return {'userprofile' : defaults }
