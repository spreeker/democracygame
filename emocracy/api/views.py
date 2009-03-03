import re
from emocracy_core.models import Votable, IssueBody
from django.shortcuts import render_to_response
from django.http import Http404, HttpResponse, HttpResponseNotAllowed
from django.core import serializers
from django.utils import simplejson
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.contrib.auth.decorators import login_required


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

# ------------------------------------------------------------------------------

def paginator_helper(request, l, paginate_by = 10):
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
    def GET(self, request, *args, **kwargs):
        raise Http404('GET')

class IssueCollection(Resource):
    def POST(self, request, *args, **kwargs):
        # The authentication check should be moved to django-oauth ASAP
        if not request.user.is_authenticated():
            return HttpResponseUnauthorized()
        # Process the POST data, using a form. If valid -> create an issue.
        # Use a Reponse with status_code 201 and URI of new issue as reply on 
        # succes.
        #IssueCreationForm()
        
        raise Http404('POST')
    
    def GET(self, request, *args, **kwargs):
        """Send paginated list of issue URIs to client as JSON."""
        # If ValueListQuerySets are evaluated to a lists by Django the following
        # line needs to change (TODO find out):
        votable_ids = Votable.objects.values_list('pk', flat = True) 
        current_page, page_no = paginator_helper(request, votable_ids, 10)
        
        resource_uris = [TEMP_SERVER_NAME + u'/api/issue/' + unicode(id) + u'/' for id in current_page.object_list]
        response_content = {'issues' : resource_uris,}
        if current_page.has_next():
            response_content['next'] = TEMP_SERVER_NAME + u'/api/issue/?page=' + unicode(current_page.next_page_number())
        if current_page.has_previous():
            response_content['previous'] = TEMP_SERVER_NAME + u'/api/issue/?page=' + unicode(current_page.previous_page_number())
            
        reply = simplejson.dumps(response_content)
        return HttpResponse(reply, mimetype = 'text/html') 
        # text/html is here for debugging, should be application/javascript or application/json

    