import re
import datetime

from django.shortcuts import render_to_response
from django.http import Http404
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseServerError, HttpResponseNotFound, HttpResponseBadRequest
from django.core import serializers
from django.utils import simplejson
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse


from voting.models import Issue
from voting.models import Vote 
from voting.models import TaggedIssue
from voting.models import Tag
from issues_content.models import IssueBody
from gamelogic import actions
from forms import IssueCollectionForm, IssueVoteCollectionForm


# BIG TODO ITEM, only send http 200 (OK) if needed and embed the http status in
# the message body. This must be done for flash / javascript apps running inside
# of a browser. See the Twitter API suppress_reponse_codes option.

# TODO research how to deal with language issues in the API.

# Useful information related to REST API design / implementation

# HTTP methods:
# http://www.w3.org/Protocols/rfc2616/rfc2616-sec9.html
# HTTP response status codes:
# http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html
# http request / response implementation in Django:
# http://docs.djangoproject.com/en/dev/ref/request-response/
# HTTP response headers:
# http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html

# ------------------------------------------------------------------------------
# Some extra response codes not defined in:
# http://code.djangoproject.com/browser/django/tags/releases/1.0.2/django/http/__init__.py

class HttpResponseUnauthorized(HttpResponse):
    status_code = 401

class HttpResponseCreated(HttpResponse):
    status_code = 201

# ------------------------------------------------------------------------------

http_verbs = ('GET', 'POST') # Not exhaustive! Just what Emocracy uses for now.
nonalpha_re = re.compile('[^A-Z]')

class RESTResource(object):
    def __call__(self, request, *args, **kwargs):
        """Dispatch based on http method. Subclasses define methods with the 
        names of http methods that they handle."""
        # Based on Django Snippet 1071 by Simon Willison.
        method = nonalpha_re.sub('', request.method.upper())
        if not method in http_verbs or not hasattr(self, method):
            allowed_methods = [x for x in http_verbs if hasattr(self, x)]
            return HttpResponseNotAllowed(allowed_methods)
        return getattr(self, method)(request, *args, **kwargs)

class RESTCollection(RESTResource):
    """This class can be used as the base class for REST API Collection views. 
    It provides a few helper methods to help with pagination and the like.
    Subclasses need to provide their own GET POST etc views."""
    
    def _paginator_helper(self, request, object_ids, paginate_by):
        """This helper function deals with the django paginator and its page= GET
        parameter."""
        paginator = Paginator(object_ids, paginate_by)
        try:
            page_no = int(request.GET.get('page', '1'))
        except ValueError:
            page_no = 1
        try:
            current_page = paginator.page(page_no)
        except (EmptyPage, InvalidPage):
            current_page = paginator.page(paginator.num_pages)
            page_no = paginator.num_pages
        return current_page, page_no

    def _paginated_collection_helper(self, request, object_ids, collection_base_URI, url_name_pk, paginate_by = 10):
        """This function constructs a dictionary with URIs to resources and
        the URIs of the next and previous page of URIs. 
        
        Assumes that the url conf to a single resource expects a keyword argument
        called pk.
        """
            
        current_page, page_no = self._paginator_helper(request, object_ids, paginate_by)
        server_base_name = u'http://' + request.META['HTTP_HOST']
        
        data = {'resources' : [server_base_name + reverse(url_name_pk, args = [pk]) for pk in current_page.object_list]}
        if current_page.has_next():
            data['next'] = server_base_name + collection_base_URI + u'?page=%d' % (page_no + 1,)
        if current_page.has_previous():
            data['previous'] = server_base_name + collection_base_URI + u'?page=%d' % (page_no - 1,)
        return data
    

# ------------------------------------------------------------------------------

class IssueResource(RESTResource):
    # show issue detail
    def GET(self, request, pk, *args, **kwargs):
        try:
            issue = Issue.objects.get(pk = pk)
        except Issue.DoesNotExist:
            return HttpResponseNotFound()
        data = {
            'title' : issue.title,
            'body' : issue.payload.body,
            'owner' :  u'http://' + request.META['HTTP_HOST'] + reverse('api_user_pk', args = [issue.owner_id]), # convert to link to User Resource
            'source_type' : issue.payload.source_type,
            'url' : issue.payload.url,
            'time_stamp' : unicode(issue.time_stamp),
        }
        return HttpResponse(simplejson.dumps(data, ensure_ascii = False), mimetype = 'text/html; charset=utf-8')
        
        
class IssueCollection(RESTCollection):
    def _sort_order_helper(self, request):
        """Helper function that checks the HTTP GET parameters for sort_order 
        this collection URI."""
        
        order_choices = ["votes", "score", "time_stamp", "hotness"]
        default_sort_order = "time_stamp"
        try:
            sort_order = request.GET["sort_order"]
        except KeyError:
            sort_order = default_sort_order
        else:
            if not sort_order in order_choices:
                sort_order = default_sort_order
        return sort_order

    def POST(self, request, *args, **kwargs):
        # The authentication check should be moved to django-oauth ASAP
        if not request.user.is_authenticated():
            return HttpResponseUnauthorized()
        form = IssueCollectionForm(request.POST)        
        # For now CSRF is turned off, django 1.1 it can be turned off on a per
        # view basis.
        if form.is_valid():
            new_issue = actions.propose(
                request.user, 
                form.cleaned_data['title'],
                form.cleaned_data['body'],
                form.cleaned_data['vote_int'],
                form.cleaned_data['source_url'],
                form.cleaned_data['source_type'],
            )
            if new_issue:
                # If a new resource is created succesfully send a 201 response and
                # embed a pointer to the newly created resource.
                data = {'resource' :  u'http://' + request.META['HTTP_HOST'] + reverse('api_issue_pk', args = [new_issue.pk]),}
                return HttpResponseCreated(simplejson.dumps(data, ensure_ascii = False), mimetype = 'text/html; charset=utf-8')
        return HttpResponseBadRequest()
        
    
    def GET(self, request, *args, **kwargs):
        """Send paginated list of issue URIs to client as JSON."""
        # If ValueListQuerySets are evaluated to a lists by Django the following
        # line needs to change (TODO find out):
        sort_order = self._sort_order_helper(request)
        print sort_order
        issue_ids = Issue.objects.order_by(sort_order).reverse().values_list('pk', flat = True)
        data = self._paginated_collection_helper(request, issue_ids, reverse('api_issue'), 
            'api_issue_pk')
        return HttpResponse(simplejson.dumps(data), mimetype = 'text/plain; charset=utf-8')
        # text/html is here for debugging, should be application/javascript or application/json

class IssueVoteCollection(RESTCollection):
    def GET(self, request, pk, *args, **kwargs):
        try:
            issue = Issue.objects.get(pk = pk)
        except Issue.DoesNotExist:
            return HttpResponseNotFound()
        # Check wether a user is in a public office, if so => all votes are public
        vote_ids = Vote.objects.filter(issue = issue, keep_private = False, is_archived = False).values_list('pk', flat = True)
        data = self._paginated_collection_helper(request, vote_ids, reverse('api_issue_pk_vote', args = [pk]), 'api_vote_pk')
        return HttpResponse(simplejson.dumps(data), mimetype = 'text/html; charset=utf-8')

    def POST(self, request, pk, *args, **kwargs):
        try:
            issue = Issue.objects.get(pk = pk)
        except Issue.DoesNotExist:
            return HttpResponseNotFound()
        form = IssueVoteCollectionForm(request.POST)
        # TODO deal with authentication correctly (that is through Oauth)
        if not request.user.is_authenticated():
            return HttpResponseNotAllowed()
        if form.is_valid():
            new_vote = actions.vote(
                request.user, 
                issue,
                form.cleaned_data['vote_int'],
                False
                )
            data = {
                'resource' : 'http://' + request.META['HTTP_HOST'] + reverse('api_vote_pk', args = [new_vote.pk])
            }
            return HttpResponseCreated(simplejson.dumps(data), mimetype = 'text/html; charset=utf-8')
        return HttpResponseBadRequest()
        
        

class IssueVoteUserResource(RESTResource):
    def GET(self, request, issue_pk, user_pk, *args, **kwargs):
        try:
            issue = Issue.objects.get(pk = issue_pk)
        except Issue.DoesNotExist:
            return HttpResponseNotFound()
        try:
            user = User.objects.get(pk = user_pk)
        except User.DoesNotExist:
            return HttpResponseNotFound()
        vote = Vote.objects.filter(owner = user, issue = issue, is_archived = False).order_by('time_stamp').reverse()
        if vote:
            data = {
                'resource' : u'http://' + request.META['HTTP_HOST'] + reverse('api_vote_pk', args = [vote[0].pk]),
            }
            return HttpResponse(simplejson.dumps(data), mimetype = 'text/html; charset=utf-8')
        else:
            return HttpResponseNotFound()

class IssueTagCollection(RESTCollection):
    def GET(self, request, pk, *args, **kwargs):
        try:
            issue = Issue.objects.get(pk = pk)
        except Issue.DoesNotExist:
            return HttpResponseNotFound()
        # TODO look at the way the Tag objects are found, see wether that
        # can be done more cleanly (/better /faster). Probably through some 
        # custom SQL ... (in gamelogic.models ).
        tag_ids = Tag.objects.get_for_issue(issue, 100).values_list('pk', flat = True)
        data = self._paginated_collection_helper(request, tag_ids, reverse('api_issue_pk_tag', args = [pk]), 'api_tag_pk')
        return HttpResponse(simplejson.dumps(data), mimetype = 'text/html; charset=utf-8')


class TagResource(RESTResource):
    def GET(self, request, pk, *args, **kwargs):
        try:
            tag = Tag.objects.get(pk = pk)
        except:
            return HttpResponseNotFound()
        data = {
            'tagname' : tag.name,
            'count' : tag.count,
        }
        return HttpResponse(simplejson.dumps(data), mimetype = 'text/html; charset=utf-8')

class VoteCollection(RESTCollection):
    def GET(self, request, *args, **kwargs):
        object_ids = Vote.objects.values_list('pk', flat = True) 
        data = self._paginated_collection_helper(request, object_ids, reverse('api_vote'),
            'api_vote_pk')
        return HttpResponse(simplejson.dumps(data), mimetype = 'text/html; charset=utf-8') 
            
class VoteResource(RESTResource):
    def GET(self, request, pk, *args, **kwargs):
        try:
            vote = Vote.objects.get(pk = pk)
        except Issue.DoesNotExist:
            return HttpResponseNotFound()
        data = {
            'vote_int' : vote.vote,
            # The vote.issue_id does not follow the relation (would cause 
            # extra and unnecessary work for the db).
            'issue' :  u'http://' + request.META['HTTP_HOST'] + reverse('api_issue_pk', args = [vote.issue_id]),
            'issueset' : 'NOT IMPLEMENTED YET',
        }
        return HttpResponse(simplejson.dumps(data, ensure_ascii = False), mimetype = 'text/html; charset=utf-8')

class UserCollection(RESTCollection):
    def GET(self, request, *args, **kwargs):
        object_ids = User.objects.values_list('pk', flat = True)
        data = self._paginated_collection_helper(request, object_ids, reverse('api_user'),
            'api_user_pk')
        return HttpResponse(simplejson.dumps(data), mimetype = 'text/html; charset=utf-8') 
        

class UserResource(RESTResource):
    def GET(self, request, pk, *args, **kwargs):
        try:
            user = User.objects.get(pk = pk)
        except User.DoesNotExist:
            return HttpResponseNotFound()
        userprofile = user.get_profile()
        data = {
            'username' : user.username,
            'score' : userprofile.score,
        }
        return HttpResponse(simplejson.dumps(data, ensure_ascii = False), mimetype = 'text/html; charset=utf-8')
        
# ------------------------------------------------------------------------------
