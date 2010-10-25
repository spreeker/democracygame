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
from tagging.models import Tag
from tagging.utils import calculate_cloud

from gamelogic import actions
from issue.models import Issue
from issue.forms import IssueForm, Publish, TagForm
from voting.managers import possible_votes, blank_votes, vote_annotate
from voting.models import Vote
from voting.views import vote_on_object
from voting.vote_types import normal_votes
from django.db.models import Count, Avg, Sum 


def paginate(request, queryset, pagesize=8):
    paginator = Paginator(queryset, pagesize)
    try:
        pageno = int(request.GET.get('page', '1'))
    except ValueError:
        pageno = 1
    try:
        page = paginator.page(pageno)
    except (EmptyPage, InvalidPage):
        page = paginator.page(paginator.num_pages) #last page
    return page

def paginate_issues(request, votes, issues):
        """ shrinks the issues queryset using a paginated
            vote queryset. 
        """
        page = paginate(request, votes, 8)
        object_ids = [ d['object_id'] for d in page.object_list ] #d = direction.
        issues = issues.filter(id__in=object_ids)
        return page, issues


def order_issues(request, sortorder, issues, min_tv=6, subset=None):
    """
    return page and queryset of issues derived from voting data. 
    
    returns issues ordered by
        popularity - issues with a lot of votes.
        controversiality - vote for/agains = 50/50
        for     - mostpeople vote for.
        against -issues most people vote against.
        new     -issues you have not voted on.
        unseen  -issues you have not seen.

    *min_tv*  minimal total votes. only issues are considered which have
        min_tv amount of votes.
    
    *subset*  if you want to run the vote management functions on a smaller
        subset of votes derived from the given issues, set to True. dont set this
        on true is issues not filtered.

    we are trying to do some aggegration using gfk's. Which is
    not easy to do or look at:
    http://github.com/coleifer/django-simple-ratings/tree/master/ratings
    or tagging generic! this approach is slow we take a different approach:
    
    Currenty we use the voting managers functions for a sorted vote queryset.
    We paginate the vote queryset. From this vote queryset we use 
    the object_ids and score field to get and sort the relevant issues.

    we return a page object and issue queryset to display on the page.
    we dont use the page.object_list because those are not always issues
    and could well be votes.
    """
    issue_ids = None
    if subset:
        issue_ids = issues.values_list('id')

    #sort issue on their vote score value.
    def _sort_issues(votes, issues,):
        scores = [(v['score'], v['object_id'],) for v in votes.all()] 
        #scores.sort()
        id_issue = dict((issue.id, issue) for issue in issues)
        sorted_issues = []
        for score, id in scores:
            issue = id_issue.get(id, False) # it is possible to have hidden issues in the score.
            if issue:
                sorted_issues.append(issue)
        return sorted_issues

    if sortorder == 'popular':
        votes = Vote.objects.get_popular(Issue, object_ids=issue_ids, min_tv=min_tv)
        page, issues = paginate_issues(request, votes, issues)
        issues = _sort_issues(page.object_list, issues)
        return page, issues
    elif sortorder == 'controversial':
        votes = Vote.objects.get_controversial(Issue, object_ids=issue_ids, min_tv=min_tv)
        return paginate_issues(request, votes, issues)
    elif sortorder == 'for':
        votes = Vote.objects.get_top(Issue, object_ids=issue_ids, min_tv=min_tv)
        page, issues = paginate_issues(request, votes, issues)
        issues = _sort_issues(page.object_list, issues)
        return page, issues
    elif sortorder == 'against':
        votes = Vote.objects.get_bottom(Issue, object_ids=issue_ids, min_tv=min_tv)
        page, issues = paginate_issues(request, votes, issues)
        issues = _sort_issues(page.object_list, issues)
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
        issues = Issue.active.select_related().order_by('-time_stamp')

    if kwargs.get('sortorder', False):
        #pagination is now done on vote table
        min_tv = kwargs.get('min_tv', 6)
        subset = kwargs.get('subset', None)
        page, issues = order_issues(request, kwargs['sortorder'], 
            issues, min_tv, subset)

    if not page: 
        page = paginate(request, issues)
        issues = page.object_list

    #XXX to be changed.
    flash_msg = request.session.get("flash_msg","")
    if flash_msg:
        del request.session['flash_msg']

    context = {'current' : 'all_issues'}
    context.update(extra_context)
    context.update({
        'blank_votes' : blank_votes.items(),
        'issues'  : issues, 
        'page' : page,
        'votedata' : Vote,
        'flash_msg' : flash_msg,
        'sortorder' : kwargs.get('sortorder', ''),
        'total_issues' : Issue.active.count(),
        'total_votes' : get_user_votes(request) 
    })

    c = RequestContext(request, context)    
    t = loader.get_template(template_name)
    return HttpResponse(t.render(c))

def get_user_votes(request):
    """ Get vote.count on active issues.
    """
    if request.user.is_authenticated():
        votes = Vote.objects.get_user_votes(request.user, Model=Issue)
        votes = votes.filter(direction__in=normal_votes.keys())
        votes = votes.filter(object_id__in=Issue.active.values_list('id',))
        return votes.count()
    return 0

def get_tagcloud_issues(issues):
    id_issues = issues.values('id') 
    issue_tags = Tag.objects.usage_for_model(Issue, 
        counts=True, filters=dict(id__in=id_issues))
    return calculate_cloud(issue_tags)


def issue_list_with_tag(request, tag=None, sortorder=None):
    """
    For a tag. display list of issues
    """
    if tag:
        stag = "\"%s\"" % tag 
        issues = Issue.tagged.with_any(stag)
        issues = issues.filter(is_draft=False)
        return issue_list(
            request, 
            issues=issues,
            sortorder=sortorder,
            min_tv=1,
            subset=True,
            extra_context = {
                'selected_tag' : tag,
                'issue_tags' : get_tagcloud_issues(issues),
                'sort_url' : reverse('issue_with_tag', args=[tag,]),
            })
    else:
        return issue_list(request)


def issue_list_user(request, username, sortorder=None):
    """ 
    For a user, specified by the ``username`` parameter, show his / her issues.
    """ 
    user = get_object_or_404(User, username=username)
    issues = Issue.active.filter(user=user.id)
    issues = issues.select_related()
    return issue_list(
        request, 
        issues=issues,
        sortorder=sortorder,
        min_tv=1,
        subset=True,
        extra_context = {
            'username': username,
            'issue_tags' : get_tagcloud_issues(issues),
            'sort_url' : reverse('issue_list_user', args=(username,)),
        }
    )


def issues_list_laws(request, sortorder=None): 
    """
    sow all issues which are law.
    """
    issues = Issue.laws.all()
    issues = issues.select_related()

    return issue_list(
        request, 
        #template_name='issue/issue_list_laws.html',
        issues=issues,
        sortorder=sortorder,
        min_tv=0,
        subset=True,
        extra_context = {
            'issue_tags' : get_tagcloud_issues(issues),
            'sort_url' : reverse('laws'),
            'current' : 'laws',
            'total_laws' : issues.count(),
        })

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
        extra_context={
            'issueform' : issueform,
            'showurl' : True,
            'sort_url' : reverse('my_issues'),
            'current' : 'my_issues',
            
        }
    )


def single_issue(request, title):
    """
    Show a single issue, with a lot of detail
    and with slugfield url
    """
    issue = get_object_or_404(Issue, slug=title)

    return issue_list(
        request, issues=[issue],
        extra_context={'showurl' : True}, #show the external url
        )

def search_issue(request):
    slug = request.GET.get('searchbox', "")
    issues = Issue.objects.filter(is_draft=False, title__icontains=slug)
    issues = issues.select_related()
    #logging.debug(issues)
    return issue_list(
        request, 
        #template_name='issue/search.html',
        issues=issues,
        subset=True,
        )

def xhr_search_issue(request,):
    """
    Search view for js autocomplete.

    'title' - string of at least 2 characters or none.
    """
    if request.method != 'GET':
        return json_error_response(
        'XMLHttpRequest search issues can only be made using GET.')

    title = request.GET.get('term', '')

    results = [] 
    if len(title) > 2:
        issue_result = Issue.objects.filter(is_draft=False,
            slug__icontains=title) 
        results = [ i.title for i in issue_result[:100]]
        
    return HttpResponse(simplejson.dumps(results), mimetype='application/json') 

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

