import logging
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseServerError
from django.http import Http404, HttpResponseRedirect,HttpResponseBadRequest 
from django.shortcuts import render_to_response, get_object_or_404
from django.template import loader, RequestContext
from django.core.urlresolvers import reverse
from django.views.generic.list_detail import object_list
from django.contrib.contenttypes.models import ContentType

from gamelogic import actions
from democracy.issue.models import Issue
from democracy.voting.managers import possible_votes 
from democracy.voting.models import Vote
from democracy.voting.views import vote_on_object
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
    template_name= "dashboard/issue_list.html"

    def objects(self):
        # you want to override this method, # must return queryset
        return Issue.objects.filter().select_related().order_by('-time_stamp')

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
            'possible_votes' : possible_votes,
            'issues'  : self.objects(),# qs 
            'actions' : actions.get_actions(request.user),
            'missing_actions' : actions.get_unavailable_actions(request.user),
            'vote' : Vote,
        }) 
       
        t = loader.get_template(self.template_name)
        return HttpResponse(t.render(c))

index = GameView()


def record_vote(request, issue_id ):
    """
    Wrapper function for the voting.views.vote_on_object function

    what if user is anonymous?

    """
    if request.REQUEST.has_key('direction'):
        direction = request.REQUEST['direction']
        return vote_on_object(request, Issue, direction , object_id=issue_id ) 
    return HttpResponseBadRequest

def record_multiply(request , issue_id ):
    """
    Wrapper funtion around gamelogic.actions.multiply
    """
    if not request.method == "POST": 
        return HttpResponseBadRequest()
    issue = get_object_or_404( Issue, id=issue_id ) 

    possible_actions = actions.get_actions(request.user) 
    message = "You cannot multiply yet!"
    next = request.REQUEST.get('next' , '/' )

    if possible_actions.has_key('multiply') :
        actions.multiply( request.user, issue )
        return HttpResponseRedirect(next)

    request.user.message_set.create(message=message)    
    return HttpResponseRedirect( next )

