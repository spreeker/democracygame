# Create your views here.
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from oauth_consumer import EmoOAuthConsumerApp

emoauth = EmoOAuthConsumerApp()

@emoauth.require_access_token
def index(request):
    return HttpResponseRedirect(reverse("top_level_menu"))
    
