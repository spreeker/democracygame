import re
from django.shortcuts import render_to_response
from django.http import Http404
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseServerError, HttpResponseNotFound, HttpResponseBadRequest
from django.core import serializers
from django.utils import simplejson
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse


from emocracy_core.models import Votable, IssueBody
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

def paginator_helper(request, l, paginate_by = 10):
    """This function contains the Paginator boilerplate ... """
    paginator = Paginator(l, paginate_by)
    try:
        page_no = int(request.GET.get('page', '1'))
    except ValueError:
        page_no = 1
    try:
        current_page = paginator.page(page_no)
    except (EmptyPage, InvalidPage):
        current_page = paginator.page(paginator.num_pages)
    return current_page, page_no

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
            issue = Votable.objects.filter(pk = pk)
        except Votable.DoesNotExist:
            return HttpResponseNotFound
        return HttpResponse(serializers.serialize("json", issue, ensure_ascii = False), mimetype = 'text/html')
        
        
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
        current_page, page_no = paginator_helper(request, votable_ids, 10)
        
        resource_uris = [TEMP_SERVER_NAME + reverse('api_issue_pk', args = [id]) for id in current_page.object_list]
    
        response_content = {'issues' : resource_uris,}
        if current_page.has_next():
            response_content['next'] = TEMP_SERVER_NAME + reverse('api_issue') + u'?page=' + unicode(current_page.next_page_number())
        if current_page.has_previous():
            response_content['previous'] = TEMP_SERVER_NAME +reverse('api_issue') + unicode(current_page.previous_page_number())
            
        reply = simplejson.dumps(response_content)
        return HttpResponse(reply, mimetype = 'text/html') 
        # text/html is here for debugging, should be application/javascript or application/json

    