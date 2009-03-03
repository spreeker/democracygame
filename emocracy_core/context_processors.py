# by Thijs Coenen for the Emocracy project october 2008
from emocracy.accounts.views import create_userprofile

def profile(request):
    if request.user.is_authenticated():
        return {'userprofile' : request.user.get_profile()}
    else:
        return {}