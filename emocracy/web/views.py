# By Thijs Coenen for the Emocracy project (october 2008).
from __future__ import division
import datetime
import logging

# TODO clean up by now unused imports ...
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404, get_list_or_404
from django.http import HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
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


from util import *
import gamelogic.actions, anonymous_actions
from web.forms import TagForm, CastVoteFormFull, IssueFormNew, HiddenOkForm, TagSearchForm, TagForm2
from web.forms import NormalVoteForm, BlankVoteForm
from emocracy.gamelogic.models import votes_to_description
from emocracy.gamelogic.models import IssueTag, TaggedIssue
from emocracy.gamelogic.models import Issue, IssueBody, IssueSet
import settings

# ------------------------------------------------------------------------------
# -- Vote related view functions : ---------------------------------------------

def vote_list_user(request, user_name):
    user = get_object_or_404(User, username = user_name)
    if request.user.username == user_name:
        user_votes = Vote.objects.filter(owner = user, is_archived = False).order_by("time_stamp").reverse()
    else:
        user_votes = Vote.objects.filter(owner = user, is_archived = False, keep_private = False).order_by("time_stamp").reverse()
    return object_list(request, queryset = user_votes, paginate_by = 25)

# ------------------------------------------------------------------------------
# -- View functions that show several Issues : ---------------------------------

class ListIssueBaseView(object):
    """This is the baseclass for the views that show several issues on 1 page.
    Subclasses can define their own get_extra_context_and_queryset to do
    filtering, set the page title and anything else that needs adding to the
    template context.
    """
    
    def get_extra_context_and_queryset(self, request, *args, **kwargs):
        """Extra filtering of the Issue queryset and setting of extra context
        paramaters is done in this instance method. Override in subclass if
        necessary."""
        extra_context = {'page_title' : _(u'All Issues')}
        queryset = Issue.objects.all()
        return extra_context, queryset
    
    def __call__(self, request, *args, **kwargs):
        """
        View instance method that does does all the standard things for
        Issue list views.
        """
        sort_order = issue_sort_order_helper(request)
        extra_context, qs = self.get_extra_context_and_queryset(request, *args, **kwargs)
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
        # grab the tags for each Issue
        tags_for_objects = [IssueTag.objects.get_for_issue(x) for x in current_page.object_list]
        
        extra_context.update({
            'sort_order' : sort_order,
            'current_page' : current_page,
            'num_pages' : paginator.num_pages,
            'show_more_info_link' : True,
            'object_list' : zip(current_page.object_list, user_votes, vote_css_class, tags_for_objects),
        })
        return render_to_response('web/issue_list_new.html',
            RequestContext(request, extra_context))

issue_list = ListIssueBaseView()

class IssuesForTagView(ListIssueBaseView):
    """
    This class shows the Issues that go with a certain tag in Emocracy.
    """
    def get_extra_context_and_queryset(self, request, *args, **kwargs):
        tag_pk = kwargs.pop('tag_pk')
        tag = get_object_or_404(IssueTag, pk = tag_pk)
        queryset = tag.get_issues()
        extra_context = {'page_title' : _(u'Issues tagged with %(tagname)s' % {'tagname' : tag.name})}
        return extra_context, queryset

issue_list_tag = IssuesForTagView()

class IssuesForUserView(ListIssueBaseView):
    """
    This class show the Issues that go with a certain user of Emocracy.
    """
    def get_extra_context_and_queryset(self, request, *args, **kwargs):
        username = kwargs.pop('username')
        user = get_object_or_404(User, username = username)
        queryset = Issue.objects.filter(owner = user)
        extra_context = {'page_title' : _(u'Issues for %(username)s' % {'username' : username})}
        return extra_context, queryset
    
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

    # TODO FIXME XSS make the handling of request parameters safe, as it stands
    # the request parameters end up in the page HTML unescaped! (that sucks!)
    
    def clean_request_parameters(self, request):
        """This method checks and cleans up request parameters, so that they are
        quaranteed to be safe to include into HTML."""
        qd = request.GET.copy()
        new_qd = QueryDict()

        if qd.has_key('form_type'):
            if qd['form_type'] in ['voteblankform', 'voteform', 'tagform']:
                new_qd['form_type'] = qd['form_type']
        if qd.has_key('page'):
            try:
                int(qd['page'])
            except ValueError:
                pass
            else:
                new_qd['page'] = qd['page']
        return new_qd
    
    def handle_voteform(self, request, issue):
        if request.method == 'POST':
            qd = clean_request_parameters(request)
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
                        gamelogic.actions.vote(request.user, issue, form.cleaned_data['vote'], False) # TODO: deal with private votes
                    else:
                        anonymous_actions.vote(request, issue, form.cleaned_data['vote'])
                    # Succesful submit of a normal (For or Against) vote,
                    # redirect to a formless version of the same page. (ie.
                    # remove formtype query parameter).
                    del qd['form_type']
                    return None, HttpResponseRedirect(request.path + '?' + qd.urlencode())
        else:
            form = NormalVoteForm()
        return form, None
                   
    def handle_voteblankform(self, request, issue):
        if request.method == 'POST':
            qd = clean_request_parameters(request)
            form = BlankVoteForm(request.POST)
            if form.is_valid():
                # Register the vote in the DB and assign score
                if request.user.is_authenticated():
                    gamelogic.actions.vote(request.user, issue, form.cleaned_data['motivation'], False) # TODO: deal with private votes
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
            qd = clean_request_parameters(request)
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


class PollTakeView(OneIssueBaseView):
    def __call__(self, request, pk, *args, **kwargs):
        poll = get_object_or_404(IssueSet, pk = pk)
        issues = poll.issues.select_related() # TODO should be cached !
        paginator = Paginator(issues, 1)
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
            
        if request.user.is_authenticated():
            votes, css = vote_helper_authenticated(request.user, current_page.object_list)
        else:
            votes, css = vote_helper_anonymous(request, current_page.object_list)
        
        # Find out what type of form to show (if any) by looking at the request
        # parameters / and deal with the forms:
        form_type = request.GET.get('form_type', '')
        if form_type == 'voteform':
            form, redirect = self.handle_voteform(request)
            if redirect: return redirect
        elif form_type == 'voteblankform':
            form, redirect = self.handle_voteblankform(request)
            if redirect: return redirect
        elif form_type == 'tagform':
            form, redirect = self.handle_tagform(request)
            if redirect: return redirect
        else:
            pass
        
        extra_context = {
            'issue' : current_page.object_list[0],
            'vote_class' : css[0],
            'vote_text' : votes[0],
            'page_title' : u'TAKE A POLL',
            'poll_pk' : poll.pk,
            'current_page' : current_page,
            'num_pages' : paginator.num_pages,
            'tags' : IssueTag.objects.get_for_issue(current_page.object_list[0]),
        }        
         
        if form_type in ['voteform','voteblankform', 'tagform']:
            extra_context[form_type] = form 
        return render_to_response('web/issue_detail.html',
            RequestContext(request, extra_context))

poll_take = PollTakeView()


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
            'tags' : IssueTag.objects.get_for_issue(issue)
        }        
        if form_type in ['voteform','voteblankform', 'tagform']:
            extra_context[form_type] = form
        
        return render_to_response('web/issue_detail.html',
            RequestContext(request, extra_context))
        
newdetail = DetailView()

# ------------------------------------------------------------------------------

@login_required
def issue_propose(request):
    """
    This view handles proposing new issues.
    """
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
            )

            return HttpResponseRedirect(reverse('issue_detail', args = [new_issue.pk]))
    else:
        form = IssueFormNew()
        
    context = RequestContext(request, {"form" : form})
    return render_to_response("web/issue_propose.html", context)

# ------------------------------------------------------------------------------
# -- Poll related view functions : ---------------------------------------------

def poll_list(request): # replace with a generic view, called straight from urls.py
    all_polls = IssueSet.objects.all().order_by("time_stamp").reverse()
    return object_list(request, queryset = all_polls, paginate_by = 25, template_name = 'web/poll_list.html')

class PollResultView(object):
    """
    Base class for all the poll result views. Override the __call__ function to
    change the template or calculation that goes with a poll.
    """
    
    def FROMDB(self, user, issue_ids):
        """
        This method extracts votes on a poll for a certain user.
        """
        out = {}
        votes = Vote.objects.filter(is_archived = False).filter(issue__in = issue_ids).filter(owner = user).values('issue', 'vote')
        for x in votes:
            out[int(x['issue'])] = int(x['vote'])
        return out
    
    def FROMSESSION(self, request, issue_ids):
        """
        This method extracts votes on a poll for a certain anonymous user
        playing Emocracy through the web interface.
        """
        out = {}
        if request.session.has_key('vote_history'):
            for pk in issue_ids:
                try:
                    out[pk] = request.session['vote_history'][pk]
                except KeyError:
                    pass
        return out        

    def __call__(self, request, poll_no):
        """
        Implementation for the 'stemwijzer' inspired polling system. Override
        this method for different 
        """
        poll_no = int(poll_no)
        poll = get_object_or_404(IssueSet, pk = poll_no)
        issue_ids = poll.issues.values_list('pk', flat = True)
                
        if request.user.is_authenticated():
            votes_on_poll = self.FROMDB(request.user, issue_ids)
        else:
            votes_on_poll = self.FROMSESSION(request, issue_ids)        

        poll_users = list(poll.users.all())
        scored_poll_users = []
        for u in poll_users:
            tmp_votes = self.FROMDB(u, issue_ids) # TODO cache this (should not change to often)
            agreement_score = 0
            disagreement_score = 0
            for pk in issue_ids:
                v1 = votes_on_poll.get(pk, None)
                v2 = tmp_votes.get(pk, None)
                if v1 in [-1, 1] and v2 in [-1, 1]:
                    # both votes are `normal'
                    if v1 == v2:
                        agreement_score += 1
                    else:
                        disagreement_score += 1
                elif v1 >= 10 and v2 >= 10:
                    # both votes are `blank'
                    # assumes blank votes start at 10 !
                    if v1 == v2:
                        agreement_score += 1
                elif v1 == None and v2 == None:
                    # both did not vote
                    pass
            scored_poll_users.append((
                int(100 * agreement_score / len(issue_ids)),
                int(100 * disagreement_score / len(issue_ids)),
                u
            ))
  
        context = RequestContext(request, {
            'poll' : poll,
            'scored_poll_users' : scored_poll_users,
            'number_of_issues' : len(issue_ids),
        })
        return render_to_response('web/poll_result.html', context)

poll_result = PollResultView()

# ------------------------------------------------------------------------------
# -- Tagging related view functions --------------------------------------------

def tagform(request, issue_pk):
    """
    This view returns an HTML fragment containing a TagForm instance.
    This view exists to serve asynchrounous javascript on the client side.
    """
    pk = int(issue_pk)
    form = TagForm({'issue_no' : pk})
    popular_tags = IssueTag.objects.get_popular(10)
    extra_context = RequestContext(request, {
        'form' : form,
        'tags' : popular_tags,
    })
    context = RequestContext(request, extra_context)
    return render_to_response('web/tagform.html', context)

def ajaxtag(request, pk):
    """
    This view handles jQuery enhanced and submitted through ajax calls to the
    tagging system.
    """
    pk = int(pk)
    issue = get_object_or_404(Issue, pk = pk)
    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            tag_object, msg = gamelogic.actions.tag(request.user, issue, form.cleaned_data["tags"])
            reply = simplejson.dumps({'msg' : msg}, ensure_ascii = False)
            return HttpResponse(reply, mimetype = 'application/json')
        else:
            reply = simplejson.dumps({'msg' : _(u'No tag added')}, ensure_ascii = False)
            return HttpResponse(reply, mimetype = 'application/json')

def search_tag(request):
    # TODO : fix unicode in request parameters.
    # (Conrado says it is not allowed, google does it anyway ...)
    # TODO FIXME XSS handle the way the search_string shows up in the page -
    # since that is not handled cleanly/correctly at the moment.
    """This view let's users search for tags."""
    if request.method == 'POST':
        form = TagSearchForm(request.POST)
        if form.is_valid():
            search_string = form.cleaned_data["search_string"]
        else:
            search_string = u''
    else:
        form = TagSearchForm()
        search_string = request.GET.get(u'search_string', u'')

    if not search_string == u'':
        qs = IssueTag.objects.filter(name__icontains = search_string)
    else:
        qs = IssueTag.objects.none()
    
    paginator = Paginator(qs, 20)
    
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
 
    if search_string:
        form.fields["search_string"].initial = search_string # TODO see wether this can be done more cleanly
    
    context = RequestContext(request, {
        'form' : form,
        'current_page' : current_page,
        'search_string' : search_string,
        'num_pages' : paginator.num_pages,
    })
    return render_to_response('web/search_tag.html', context)

# ------------------------------------------------------------------------------

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
            vote_int = form.cleaned_data["vote"] + form.cleaned_data["motivation"]
                        
            if vote_int == 1: 
                css_class = u'for'
            elif vote_int == -1:
                css_class = u'against'
            else:
                css_class = u'blank'

            if request.user.is_authenticated():
                gamelogic.actions.vote(request.user, issue, vote_int, form.cleaned_data['keep_private'])
            else:
                anonymous_actions.vote(request, issue, vote_int)
            
            data = {
                'issue_no' : issue_no,
                'vote_text' : votes_to_description[vote_int],
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
        

# ------------------------------------------------------------------------------

@login_required
def mandate(request, rep):
    representative = get_object_or_404(User, username = rep)
    if request.method == 'POST':
        form = HiddenOkForm(request.POST)
        if form.is_valid():
            gamelogic.actions.mandate(request.user, representative)
    form = HiddenOkForm()
    context = RequestContext(request, {
        'representative' : representative,
        'form' : form,
    })
    return render_to_response('web/mandate.html', context)

@login_required
def become_candidate(request):
    if request.method == 'POST':
        form = HiddenOkForm(request.POST)
        if form.is_valid():
            gamelogic.actions.become_candidate(request.user)
    form = HiddenOkForm()
    context = RequestContext(request, {
        'form' : form,
    })
    return render_to_response('web/become_candidate.html', context)
    