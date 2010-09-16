"""
Views for showing and acting on Issues.

Propose a new issue.
Vote on an issue
Publish hide an issue
Tag an issue
Mulitply an issue
show Issues in ordering
show User issues.
"""
import logging
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseServerError
from django.http import Http404, HttpResponseRedirect,HttpResponseBadRequest 
from django.shortcuts import render_to_response, get_object_or_404
from django.template import loader, RequestContext
from django.core.urlresolvers import reverse
from django.views.generic.list_detail import object_list
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.utils.translation import ugettext as _
from django.utils import simplejson

from tagging.forms import TagField

from gamelogic import actions
from issue.models import Issue
from issue.forms import IssueForm, Publish, TagForm
from voting.managers import possible_votes, blank_votes, vote_annotate
from voting.models import Vote
from voting.views import vote_on_object
from django.db.models import Count, Avg, Sum 


def paginate(request, qs, pagesize=8):
    paginator = Paginator(qs, pagesize)
    try:
        pageno = int(request.GET.get('page', '1'))
    except ValueError:
        pageno = 1
    try:
        page = paginator.page(pageno)
    except (EmptyPage, InvalidPage):
        page = paginator.page(paginator.num_pages) #last page
    return page


def order_issues(request, sortorder, issues, min_tv=6, subset=None):
    """
    return page and qs of issues derived from voting data. 
    
    returns issues ordered by
        popularity - issues with a lot of votes.
        controversiality - vote for/agains = 50/50
        for     - mostpeople vote for.
        against -issues most people vote against.
        new     -issues you have not voted on.

    we are trying to do some aggegration using gfk's. Which is
    not easy to do or look at:
    http://github.com/coleifer/django-simple-ratings/tree/master/ratings
    or tagging generic!

    *min_tv*  minimal total votes. only issues are considered which have
        min_tv amount of votes.
    
    *subset*  if you want to run the vote management functions on a smaller
        subset of votes derived from the given issues, set to True. dont set this
        on true is issues not filtered.
    """
    issue_ids = None
    if subset:
        issue_ids = issues.values_list('id')

    #sort issue on their vote score value.
    #this is faster then hitting the db again for an anotation.
    def _sort_issues(votes, issues,):
        scores = [(v['score'], v['object_id'],) for v in votes.all()] 
        #scores.sort()
        id_issue = dict((issue.id, issue) for issue in issues)
        return [ id_issue[id] for score, id in scores ]

    def merge_qs(votes,issues):
        """ with this method shrinks the issues qs using a paginated
            vote qs. so the vote_annotate will run fast.
        """
        page = paginate(request, votes, 8)
        object_ids = [ d['object_id'] for d in page.object_list ] #d = direction.
        issues = issues.filter(id__in=object_ids)
        return page, issues

    if sortorder == 'popular':
        votes = Vote.objects.get_popular(Issue, object_ids=issue_ids)
        page, issues = merge_qs(votes, issues)
        issues = _sort_issues(page.object_list, issues)
        #issues = vote_annotate(issues, Vote.payload, 'id', Count)
    elif sortorder == 'controversial':
        votes = Vote.objects.get_controversial(Issue, object_ids=issue_ids, min_tv=min_tv)
        return merge_qs(votes, issues)
    elif sortorder == 'for':
        votes = Vote.objects.get_top(Issue, object_ids=issue_ids, min_tv=min_tv)
        page, issues = merge_qs(votes, issues)
        #issues = vote_annotate(issues, Vote.payload, 'vote', Sum)
        issues = _sort_issues(page.object_list, issues)
        return page, issues
    elif sortorder == 'against':
        votes = Vote.objects.get_bottom(Issue, object_ids=issue_ids, min_tv=min_tv)
        page, issues = merge_qs(votes, issues)
        issues = _sort_issues(page.object_list, issues)
        #issues = vote_annotate(issues, Vote.payload, 'vote', Sum, desc=False)
    elif sortorder == 'new':
        issues = issues.order_by('-time_stamp')
    else:
        # assume 'unseen' ordering, which means finding issues for which
        # the user has no votes for.
        if request.user.is_authenticated(): 
            votes = Vote.objects.get_user_votes(request.user, Issue) #get user votes.
            votes = votes.values_list('object_id', )
            issues = issues.exclude(id__in=votes)

    return False, issues

def issue_list(request, *args, **kwargs):
    """ 
    shows issues to vote on in different sortings
    based on collective knowlegde from votings on them
    
    Note by using the keyword arguments ``template_name``, ``extra_context`` and
    ``issues`` one can reuse most or all of the display-an-issue-code (no need
    to reimplement that stuff). How to use:
    
    1 build a view function that calls and returns this view
    2 construct a QuerySet of Issues pass it in with as ``issues``
    3 save a (edited) copy of "issue/issue_list.html" somewhere
    4 pass in the template location as ``template_name``
    5 pass in a dictionary of extra context variables as ``extra_context``
    
    These keywords were added whilst constructing a page that shows a user's
    issues without reimplementing this function etc.
    """
    
    template_name = kwargs.get('template_name', "issue/issue_list.html")
    extra_context = kwargs.get('extra_context', dict())

    page = False 

    if kwargs.has_key('issues'):
        issues = kwargs['issues']
    else:
        issues = Issue.objects.select_related().order_by('-time_stamp')
        issues = issues.filter( is_draft=False )

    if kwargs.get('sortorder', False):
        #pagination is now done on vote table
        min_tv = kwargs.get('min_tv', 6)
        subset = kwargs.get('subset', None)
        page, issues = order_issues(request, kwargs['sortorder'], 
            issues, min_tv, subset)
    elif 'tag' in kwargs:
        tag = "\"%s\"" % kwargs['tag']
        issues = Issue.tagged.with_any(tag)
        issues = issues.filter( is_draft=False )

    if not page: 
        page = paginate(request, issues)
        issues = page.object_list

    flash_msg = request.session.get("flash_msg","")
    if flash_msg:
        del request.session['flash_msg']

    possible_votes.update({
        #not used in db.just for template compatibility.
        2 : _(u"Against"), # index -1 fails in templates.
        0 : _(u"Blank"),   # 0 is included to sum up all blank votes.
    })

    context = extra_context
    context.update({
        'blank_votes' : blank_votes.items(),
        'possible_votes' : possible_votes,
        'issues'  : issues, 
        'page' : page,
        'votedata' : Vote,
        'flash_msg' : flash_msg,
        'actions' : actions.get_actions(request.user),
    })

    c = RequestContext(request, context)    
    t = loader.get_template(template_name)
    return HttpResponse(t.render(c))


def issue_list_user(request, username, sortorder=None):
    """ 
    For a user, specified by the ``username`` parameter, show his / her issues.
    """ 
    user = get_object_or_404(User, username=username)
    issues = Issue.objects.filter(user=user.id)
    issues = issues.filter( is_draft=False )
    issues = issues.select_related()
    return issue_list(
        request, 
        extra_context={'username': username}, 
        template_name='issue/issue_list_user.html',
        issues=issues,
        sortorder=sortorder,
        min_tv=2,
        subset=True,
    )

@login_required
def my_issue_list(request, sortorder='new'):
    issues = Issue.objects.filter(user=request.user)
    issues = issues.filter( is_draft=False )
    issues = issues.select_related()
    issueform = propose_issue(request)
    return issue_list(
        request,
        template_name='issue/my_issue_list.html',
        issues=issues,
        sortorder=sortorder,
        min_tv=1,
        subset=True,
        extra_context={'issueform' : issueform},
    )


def single_issue(request, title):
    """
    Show a single issue, with a lot of detail
    and with slugfield url
    """
    issue = get_object_or_404(Issue, slug=title)

    return issue_list(
        request, issues=[issue],)


def record_vote(request, issue_id):
    """
    Wrapper function for the voting.views.vote_on_object function
    It does 3 cases:
        -handle anonymous votes
        -handle and validate normal direction votes. 
        -handle ajax votes
    """
    if not request.user.is_authenticated() and request.REQUEST.has_key('direction'):
        return handle_anonymous_vote(request, issue_id)
    
    if request.REQUEST.has_key('direction'):
        direction = int(request.REQUEST['direction'])
        if (not request.is_ajax()) and not possible_votes.has_key(direction):
            message = _("You did not pick a valid option")
            request.session["flash_msg"] = message
            next = request.REQUEST.get('next', '/' )
            return HttpResponseRedirect(next) 
        return vote_on_object(request, Issue, direction, object_id=issue_id, allow_xmlhttprequest=True ) 
        
    return HttpResponseRedirect('/')

def handle_anonymous_vote(request, issue_id):
    vote_history = request.session.get("vote_history", {})
    vote_history[int(issue_id)] = request.REQUEST['direction']
    request.session['vote_history'] = vote_history
    request.session.modified = True

    message = _("You voted succesfull, to save your votes please register")
    if request.is_ajax():
        issue = get_object_or_404(Issue, id=issue_id)
        return HttpResponse(simplejson.dumps({
            'succes' : True,
            'message': message,
            'score': Vote.objects.get_object_votes(issue),
            }))
    request.session["flash_msg"] = message
    next = request.REQUEST.get('next', '/' )
    return HttpResponseRedirect(next)



def record_multiply(request, issue_id ):
    """
    Wrapper funtion around gamelogic.actions.multiply
    """
    if not request.method == "POST": 
        return HttpResponseBadRequest()
    issue = get_object_or_404(Issue, id=issue_id) 

    possible_actions = actions.get_actions(request.user) 
    next = request.REQUEST.get('next', '/' )

    if possible_actions.has_key('multiply'):
        actions.multiply(request.user, issue )
        return HttpResponseRedirect(next)

    if not request.user.is_authenticated():
        return HttpResponseRedirect(next)

    message = _("You cannot multiply yet!")
    request.user.message_set.create(message=message)    
    return HttpResponseRedirect(next)


def propose_issue(request):
    """
    Wrapper for gamelogic.actions.propose
    and for gamelogic.actions.tag
    save an issue in the system possibly with tags.
    return issue form with errors data to be used in other views
    """
    form = IssueForm()

    if request.method == "POST":
        form = IssueForm(request.POST)
        if form.is_valid():
            new_issue = actions.propose(
                request.user,
                form.cleaned_data['title'],
                form.cleaned_data['body'],
                form.cleaned_data['direction'],
                form.cleaned_data['url'],
                form.cleaned_data['source_type'],
                #form.cleaned_data['is_draft'], 
                False,
            )
            if form.cleaned_data['tags']:
                actions.tag(
                    request.user,
                    new_issue,
                    form.cleaned_data['tags'],
                )
            form = IssueForm()
    return form

@login_required
def tag_issue(request, issue_id):
    """
    Tag an issue. Just Your own for now.
    returns a tag form.
    """
    issue = get_object_or_404(Issue, id=issue_id, user=request.user)
    if request.method == "POST":
        form = TagForm(request.POST)

        if form.is_valid():
            actions.tag(
                request.user,
                issue,
                form.cleaned_data['tags']
            )
    next = request.REQUEST.get('next', '/' )
    return HttpResponseRedirect(next) 


def json_error_response(error_message):
    return HttpResponse(simplejson.dumps(dict(success=False,
                    error_message=error_message)))



def xhr_publish_issue(request, issue_id):
    if request.method == 'GET':
        return json_error_response(
            'XMLHttpRequest votes can only be made using POST.')
    if not request.user.is_authenticated():
        return json_error_response('Not authenticated.')

    try:
        issue = Issue.objects.get(id=issue_id, user=request.user)
    except ObjectDoesNotExist:
        return json_error_response('No Issue found ') 

    form = Publish(request.POST)
    if form.is_valid(): 
        issue.is_draft = True if form.cleaned_data['is_draft'] else False
        issue.save()

    return HttpResponse(simplejson.dumps({
        'success': True,
    }))
    

def publish_issue(request, issue_id):
    """
    publish or not to publish issue
    """
    logging.debug("i get here") 
    if request.is_ajax():
        return xhr_publish_issue(request, issue_id)

    if request.method != "POST" or not request.user.is_authenticated():
        return HttpResponseBadRequest

    issue = get_object_or_404(Issue, id=issue_id, user=request.user)
    
    form = Publish(request.POST)

    if form.is_valid(): 
        issue.is_draft = True if form.cleaned_data['is_draft'] else False
        issue.save()

    next = request.REQUEST.get('next', '/' )
    return HttpResponseRedirect(next) 

