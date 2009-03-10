# by Thijs Coenen for the Emocracy project october 2008

def profile(request):
    """This context processor adds a user's userprofile to the context if a user
    is logged in."""
    # This context processor is used by the RequestContext, see the settings.py
    # TEMPLATE_CONTEXT_PROCESSORS variable for the other context processors.
    if request.user.is_authenticated():
        return {'userprofile' : request.user.get_profile()}
    else:
        return {}