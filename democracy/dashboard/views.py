import logging
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseServerError
from django.http import Http404, HttpResponseRedirect 
from django.template import loader, RequestContext
from django.core.urlresolvers import reverse
from django.views.generic.list_detail import object_list
from django.contrib.contenttypes.models import ContentType

from gamelogic import actions
from democracy.issue.models import Issue
from democracy.voting.managers import possible_votes 
from democracy.voting.models import Vote

# creating gameviews

class GameView(object):
    """ 
    provide the necessarily gameplaying data: 
    actions
    vote_options
    objects/issues
    issues not voted on?
    """
    # override in subclass if needed 
    objects_name = "issues"
    template_name= "issue_list.html"

    def objects(self):
        # you want to override this method
        # must return queryset
        return Issue.objects.filter().select_related()

    def __call__(self, request, *args, **kwargs):
        if request.method == "GET":
            return self.getview(request, *args, **kwargs)

    def getview(self, request, *args, **kwargs):
        blank_votes = possible_votes.copy() 
        blank_votes.pop(-1)
        blank_votes.pop(1)
        blank_votes = blank_votes.items()

        c = RequestContext(request, {
            'blank_votes' : blank_votes,
            '%s' % self.objects_name :  self.objects(),# qs 
            'actions' : actions.get_actions(request.user),
            'missing_actions' : actions.get_unavailable_actions(request.user),
        }) 
       
        t = loader.get_template(self.template_name)
        return HttpResponse(t.render(c))

index = GameView()


def vote(request):
    next = "/"
    return HttpResponseRedirect(next)
