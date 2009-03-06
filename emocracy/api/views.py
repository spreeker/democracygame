import re
from django.shortcuts import render_to_response
from django.http import Http404
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseServerError, HttpResponseNotFound, HttpResponseBadRequest
from django.core import serializers
from django.utils import simplejson
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse


from emocracy_core.models import Votable, IssueBody, Vote
from emocracy_core import actions
from forms import IssueCollectionForm


TEMP_SERVER_NAME = u'http://127.0.0.1:8000'

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

def paginated_collection_helper(request, object_ids, url_name, url_name_pk , paginate_by = 10):
    """This function constructs a dictionary with URIs to resources and
    the URIs of the next and previous page of URIs. 
    
    Assumes that the url conf to a single resource is expects a keyword argument
    called pk.
    """
    paginator = Paginator(object_ids, paginate_by)
    try:
        page_no = int(request.GET.get('page', '1'))
    except ValueError:
        page_no = 1
    try:
        current_page = paginator.page(page_no)
    except (EmptyPage, InvalidPage):
        current_page = paginator.page(paginator.num_pages)
    data = {'resources' : [TEMP_SERVER_NAME + reverse(url_name_pk, args =[pk]) for pk in current_page.object_list]}
    if current_page.has_next():
        data['next'] = TEMP_SERVER_NAME + reverse(url_name) + u'?page=%d' % (page_no + 1,)
    if current_page.has_previous():
        data['previous'] = TEMP_SERVER_NAME + reverse(url_name) + u'?page=%d' % (page_no - 1,)
    return data

# ------------------------------------------------------------------------------

http_verbs = ('GET', 'POST') # Not exhaustive! Just what Emocracy uses for now.
nonalpha_re = re.compile('[^A-Z]')

class Resource(object):
    def __call__(self, request, *args, **kwargs):
        """Dispatch based on http method. Subclasses define methods with the 
        names of http methods that they handle."""
        # Based on Django Snippet 1071 by Simon Willison.
        method = nonalpha_re.sub('', request.method.upper())
        if not method in http_verbs or not hasattr(self, method):
            allowed_methods = [x for x in http_verbs if hasattr(self, x)]
            return HttpResponseNotAllowed(allowed_methods)
        return getattr(self, method)(request, *args, **kwargs)

# ------------------------------------------------------------------------------

class IssueResource(Resource):
    # show issue detail
    def GET(self, request, pk, *args, **kwargs):
        try:
            issue = Votable.objects.get(pk = pk)
        except Votable.DoesNotExist:
            return HttpResponseNotFound()
        data = {
            'title' : issue.title,
            'body' : issue.payload.body,
            'owner' : TEMP_SERVER_NAME + u"/api/user/" + unicode(issue.owner_id) + "/", # convert to link to User Resource
            'source_type' : issue.payload.source_type,
            'url' : issue.payload.url,
            'time_stamp' : unicode(issue.time_stamp),
        }
        return HttpResponse(simplejson.dumps(data, ensure_ascii = False), mimetype = 'text/html')
        
        
class IssueCollection(Resource):
    def POST(self, request, *args, **kwargs):
        # The authentication check should be moved to django-oauth ASAP
        if not request.user.is_authenticated():
            return HttpResponseUnauthorized()
        form = IssueCollectionForm(request.POST)        
        # For now CSRF is turned off, django 1.1 it can be turned off on a per
        # view basis.
        if form.is_valid():
            new_votable = actions.propose(
                request.user, 
                form.cleaned_data['title'],
                form.cleaned_data['body'],
                form.cleaned_data['vote_int'],
                form.cleaned_data['source_url'],
                form.cleaned_data['source_type'],
            )
            if new_votable:
                # If a new resource is created succesfully send a 201 response and
                # embed a pointer to the newly created resource.
                data = {'resource' : TEMP_SERVER_NAME + reverse('api_issue_pk', args = [new_votable.pk]),}
                return HttpResponseCreated(simplejson.dumps(data, ensure_ascii = False), mimetype = 'text/html')
            else:
                return HttpReponseBadRequest()
        else:
            return HttpResponseBadRequest()
        
    
    def GET(self, request, *args, **kwargs):
        """Send paginated list of issue URIs to client as JSON."""
        # If ValueListQuerySets are evaluated to a lists by Django the following
        # line needs to change (TODO find out):
        votable_ids = Votable.objects.values_list('pk', flat = True) 
        data = paginated_collection_helper(request, votable_ids, 'api_issue', 
            'api_issue_pk')
        return HttpResponse(simplejson.dumps(data), mimetype = 'text/html') 
        # text/html is here for debugging, should be application/javascript or application/json

class VoteCollection(Resource):
    def GET(self, request):
        object_ids = Vote.objects.values_list('pk', flat = True) 
        data = paginated_collection_helper(request, object_ids, 'api_vote',
            'api_vote_pk')
        return HttpResponse(simplejson.dumps(data), mimetype = 'text/html') 
            
class VoteResource(Resource):
    def GET(self, request, pk, *args, **kwargs):
        try:
            vote = Vote.objects.get(pk = pk)
        except Votable.DoesNotExist:
            return HttpResponseNotFound()
        data = {
            'vote_int' : vote.vote,
            # The vote.votable_id does not follow the relation (would cause 
            # extra and unnecessary work for the db).
            'issue' : TEMP_SERVER_NAME + reverse('api_issue_pk', args = [vote.votable_id]),
            'votableset' : 'NOT IMPLEMENTED YET',
        }
        return HttpResponse(simplejson.dumps(data, ensure_ascii = False), mimetype = 'text/html')

class UserCollection(Resource):
    def GET(self, request, *args, **kwargs):
        object_ids = User.objects.values_list('pk', flat = True)
        data = paginated_collection_helper(request, object_ids, 'api_user', 
            'api_user_pk')
        return HttpResponse(simplejson.dumps(data), mimetype = 'text/html') 
        

class UserResource(Resource):
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
        return HttpResponse(simplejson.dumps(data, ensure_ascii = False), mimetype = 'text/html')
        