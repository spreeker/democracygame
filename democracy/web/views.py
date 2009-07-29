from __future__ import division
import datetime
import logging

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404, get_list_or_404
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.template import RequestContext
from django.views.generic.list_detail import object_list, object_detail
from django.http import Http404, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.http import HttpResponse, HttpResponseServerError
from django.utils import simplejson
from django import forms
from django.template.loader import render_to_string
from django.http import QueryDict

from util import vote_helper_anonymous
from util import vote_helper_authenticated
from util import issue_sort_order_helper

import gamelogic.actions
import anonymous_actions

from web.forms import CastVoteFormFull
from web.forms import IssueFormNew
from web.forms import HiddenOkForm
from web.forms import AuthorizeRequestTokenForm
from web.forms import NormalVoteForm
from web.forms import BlankVoteForm
from voting.models import votes_to_description
from voting.models import Issue
from voting.models import Vote
from issue.content.models import IssueBody


import settings

# ------------------------------------------------------------------------------
# -- Vote related view functions : ---------------------------------------------

def vote_list_user(request, user_name):
    user = get_object_or_404(User, username = user_name)
    if request.user.username == user_name:
        user_votes = Vote.objects.filter(owner = user, is_archived = False).order_by("time_stamp").reverse()
    else:
        user_votes = Vote.objects.filter(owner = user, is_archived = False, keep_private = False).order_by("time_stamp").reverse()
    return object_list(request, queryset = user_votes, paginate_by = 25,
        template_name = 'web/vote_list.html')

# ------------------------------------------------------------------------------
# -- View functions that show several Issues : ---------------------------------

class ListIssueBaseView(object):
    """This is the baseclass for the views that show several issues on 1 page.
    Subclasses can define their own issue_queryset to do
    issue filtering, and set the page title and anything else 
    in the self.extra_context 
    """
    extra_context = {'page_title' : _(u'All Issues')}
    
    def issue_queryset(self, request, *args, **kwargs):
        queryset = Issue.objects.all()
        return queryset

    def __call__(self, request, *args, **kwargs):
        """
        View instance method that does does all the standard things for
        Issue list views.
        """
        sort_order = issue_sort_order_helper(request)
        qs = self.issue_queryset(request , *args , **kwargs)
        queryset = qs.order_by(sort_order).reverse()
        paginator = Paginator(queryset, 5)
        
        # Grab page number from the HTTP GET parameters if present.
        try:
            page_no = int(request.GET.get('page', '1'))
        except ValueError:
            page_no = 1
        # See wether requested page is available at all from the paginator.
        try:
            current_page = paginator.page(page_no)
        except (EmptyPage, InvalidPage):
            current_page = paginator.page(paginator.num_pages)
        # grab votes from DB / session
        if request.user.is_authenticated():
            user_votes, vote_css_class = vote_helper_authenticated(request.user, current_page.object_list)
        else:
            user_votes, vote_css_class = vote_helper_anonymous(request, current_page.object_list)
        
        self.extra_context.update({
            'sort_order' : sort_order,
            'current_page' : current_page,
            'num_pages' : paginator.num_pages,
            'show_more_info_link' : True,
            'object_list' : zip(current_page.object_list, user_votes, vote_css_class, ) ,
            'actions'   : gamelogic.actions.get_actions(request.user),
            'unavailable_actions' : gamelogic.actions.get_unavailable_actions(request.user),
        })
        return render_to_response('web/issue_list.html',
                                    self.extra_context,
                                    context_instance=RequestContext(request),
                                    )

list_issues = ListIssueBaseView()


class IssuesForUserView(ListIssueBaseView):
    """
    This class show the Issues that go with a certain user of Emocracy.
    """
    def issue_queryset(self, request, *args, **kwargs):
        username = kwargs.pop('username')
        user = get_object_or_404(User, username = username)
        queryset = Issue.objects.filter(owner = user)
        self.extra_context = {'page_title' : _(u'Issues for %(username)s' % {'username' : username})}
        return  queryset
    
issues_list_user = IssuesForUserView()
    
# ------------------------------------------------------------------------------
# -- Views that show one Issue at a time : -------------------------------------

class OneIssueBaseView(object):
    """This class needs to inherited from by a class that implements __call__.
    This base class implements the non Javascript fallback voting system for
    Emocracy. It handles voting and tagging depending on the query parameter
    form_type. This the methods in this class take care to only touch the
    form_type query_parameter.
    
    In practice this view is used by the polling implementation and the detail
    views.
    
    The handle_voteform, handle_voteblankform and handle_tagform methods in this
    class all return a tuple of a form instance and a HttpReponseRedirect.
    Either the form or the HttpResponseRedirect will be None. (That information
    can then be used by the subclass to do the right thing.)
    """

    def clean_GET_parameters(self, request):
        """This method checks and cleans up GET parameters, so that they are
        guaranteed to be safe to include into HTML."""
        # Make an empty QueryDict, make it mutable (and later only add cleaned
        # key, value pairs).
        cleaned_GET_parameters = QueryDict({}).copy()
        # Check that the form to be included is for tagging, voting or giving
        # your motivation on a blank vote.
        if request.GET.has_key('form_type'):
            if request.GET['form_type'] in ['voteblankform', 'voteform', 'tagform']:
                cleaned_GET_parameters['form_type'] = request.GET['form_type']
        # Check that the page parameter is only an integer (the page parameter
        # is used for the polling view).
        if request.GET.has_key('page'):
            try:
                int(request.GET['page'])
            except ValueError:
                pass
            else:
                cleaned_GET_parameters['page'] = request.GET['page']
        # Note, any other GET parameters are discarded.
        return cleaned_GET_parameters
        
    def handle_voteform(self, request, issue):
        if request.method == 'POST':
            qd = self.clean_GET_parameters(request)
            form = NormalVoteForm(request.POST)
            if form.is_valid():
                if form.cleaned_data['vote'] == 0:
                    # Succesful submit of a blank vote, now redirect to a form
                    # that lets the user give a motivation.
                    qd['form_type'] = 'voteblankform'                        
                    return None, HttpResponseRedirect(request.path + '?' + qd.urlencode())
                else:
                    # Register the votes in the DB and assign score:
                    if request.user.is_authenticated():
                        gamelogic.actions.vote(request.user, issue, form.cleaned_data['vote'], form.cleaned_data["keep_private"]) 
                    else:
                        anonymous_actions.vote(request, issue, form.cleaned_data['vote'])
                    # Succesful submit of a normal (For or Against) vote,
                    # redirect to a formless version of the same page. (i.e.
                    # remove formtype query parameter).
                    del qd['form_type']
                    return None, HttpResponseRedirect(request.path + '?' + qd.urlencode())
        else:
            form = NormalVoteForm()
        return form, None
                   
    def handle_voteblankform(self, request, issue):
        if request.method == 'POST':
            qd = self.clean_GET_parameters(request)
            form = BlankVoteForm(request.POST)
            if form.is_valid():
                # Register the vote in the DB and assign score
                if request.user.is_authenticated():
                    gamelogic.actions.vote(request.user, issue, form.cleaned_data['motivation'], form.cleaned_data["keep_private"])
                else:
                    anonymous_actions.vote(request, issue, form.cleaned_data['motivation'])
                # Succesful submit of a motivation for a blank vote. Redirect to
                # a formless version of the same page.                
                del qd['form_type']
                return None, HttpResponseRedirect(request.path + '?' + qd.urlencode())
        else:
            form = BlankVoteForm()
        return form, None
    
    def handle_tagform(self, request, issue):
        if request.method == 'POST':        
            qd = self.clean_GET_parameters(request)
            form = TagForm2(request.POST)
            if form.is_valid():
                ptag = form.cleaned_data.get(u'popular_tags')
                tag = form.cleaned_data.get(u'tags')
                if ptag:
                    gamelogic.actions.tag(request.user, issue, ptag)
                else:
                    gamelogic.actions.tag(request.user, issue, tag)

                # New tag sucessfully submitted. Redirect to formless version
                # of this page.
                del qd['form_type']
                return None, HttpResponseRedirect(request.path + '?' + qd.urlencode())
        else:
            form = TagForm2()
        return form, None




class DetailView(OneIssueBaseView):
    def __call__(self, request, pk, *args, **kwargs):
        issue = get_object_or_404(Issue, pk = pk)
        form_type = request.GET.get('form_type', '')
        if form_type == 'voteform':
            form, redirect = self.handle_voteform(request, issue)
            if redirect: return redirect
        elif form_type == 'voteblankform':
            form, redirect = self.handle_voteblankform(request, issue)
            if redirect: return redirect
        elif form_type == 'tagform':
            form, redirect = self.handle_tagform(request, issue)
            if redirect: return redirect
        else:
            pass
        
        if request.user.is_authenticated():
            votes, css = vote_helper_authenticated(request.user, [issue])
        else:
            votes, css = vote_helper_anonymous(request, [issue])

        extra_context = {
            'issue' : issue,
            'vote_class' : css[0],
            'vote_text' : votes[0],
            'title' : u'ISSUE DETAIL VIEW',
            'clean_request_path_for_form' : request.path + u'?' + self.clean_GET_parameters(request).urlencode(),            
        }        
        if form_type in ['voteform','voteblankform', 'tagform']:
            extra_context[form_type] = form
        
        return render_to_response('web/issue_detail.html',
                                    extra_context,
                                    context_instance=RequestContext(request),
                                    )
        
issue_detail = DetailView()

# ------------------------------------------------------------------------------

@login_required
def issue_propose(request, issue_no = None):
    """
    This view handles proposing new issues.
    """
    if issue_no is not None: # view was called to edit an issue
        issue = get_object_or_404(Issue, pk = issue_no)
        try:
            # TODO
            # If users were to be allowed to change their opinion on their own
            # issue the following line needs to use a filter() instead of get().
            v = Vote.objects.get(issue = issue, owner = request.user)
            owners_direction = v.direction
        except:
            owners_direction = 1
        if issue.owner != request.user: # check that user is owner
            # TODO add is_draft check
            # TODO add more appropriate Http Response code if user tries to 
            # change an issue that is not theirs.
            raise Http404
        # TODO check type of payload in some future where there might be more 
        # than just IssueBody objects linked to Issue objects.
        issue_body = issue.payload
        # note the following ties into the IssueFormNew definition in web/forms.py
        data = {
            'title' : issue.payload.title,
            'body' : issue.payload.body,
            'url' : issue.payload.url,
            'source_type' : issue.payload.source_type,
            'owners_vote' : owners_direction,
            'is_draft': issue.is_draft
        }
    
    if request.method == "POST":
        form = IssueFormNew(request.POST)
        if form.is_valid():
        
            new_issue = gamelogic.actions.propose(
                request.user,
                form.cleaned_data[u'title'],
                form.cleaned_data[u'body'],
                form.cleaned_data[u'owners_vote'],
                form.cleaned_data[u'url'],
                form.cleaned_data[u'source_type'],
                form.cleaned_data[u'is_draft'],
                issue_no,
            )

            return HttpResponseRedirect(reverse('web_issue_detail', args = [new_issue.pk]))
    else:
        if issue_no == None:
            form = IssueFormNew()
        else:
            form = IssueFormNew(data)
        
    context = RequestContext(request, {"form" : form})
    return render_to_response("web/issue_propose.html", context)

def voteform(request, issue_no):
    """
    This view returns an HTML fragment containing a CastVoteFormFull instance.
    This view exists to serve asynchrounous javascript on the client side.
    """
    f = CastVoteFormFull({'issue_no' : int(issue_no), 'vote' : 0})
    context = RequestContext(request, {'voteform' : f})
    return render_to_response('web/voteform.html', context)


def ajaxvote(request):
    # TODO Refactor / Clean up.
    """
    This view handles voting using asynchronous javascript. View gets posted
    a voteform and returns succes / failure through http status codes and JSON.
    """
    if request.method == 'POST':
        form = CastVoteFormFull(request.POST)
        if form.is_valid(): 
            issue_no = int(form.cleaned_data["issue_no"])
            try:
                issue = Issue.objects.get(pk = issue_no)
            except:
                reply = simplejson.dumps({'msg' : _('Issue object does not exist')}, ensure_ascii = False)
                return HttpResponseServerError(reply, mimetype = 'application/javascript')            
            
            # The following line adapt the output from the vote form (old style)
            # to the new style of votes.
            direction = form.cleaned_data["vote"] + form.cleaned_data["motivation"]
                        
            if direction == 1: 
                css_class = u'for'
            elif direction == -1:
                css_class = u'against'
            else:
                css_class = u'blank'

            if request.user.is_authenticated():
                gamelogic.actions.vote(request.user, issue, direction, form.cleaned_data['keep_private'])
            else:
                anonymous_actions.vote(request, issue, direction)
            
            data = {
                'issue_no' : issue_no,
                'vote_text' : votes_to_description[direction],
                'css_class' : css_class,
                'score' : issue.score,
                'votes' : issue.votes,
            }
            reply = simplejson.dumps(data, ensure_ascii = False)
            return HttpResponse(reply, mimetype = 'application/json')
        else:
            reply = simplejson.dumps({'msg' : 'Failed to vote.'}, ensure_ascii = False)
            return HttpResponseServerError(reply, mimetype = 'application/json')
    else:
        reply = simplejson.dumps({'msg' : 'View needs to be posted to.'}, ensure_ascii = False)
        return HttpResponseServerError(reply, mimetype = 'application/json')
        

