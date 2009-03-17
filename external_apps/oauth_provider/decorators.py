from oauth.oauth import OAuthError

try:
    from functools import wraps, update_wrapper
except ImportError:
    from django.utils.functional import wraps, update_wrapper  # Python 2.3, 2.4 fallback.

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.utils.translation import ugettext as _

from utils import initialize_server_request, send_oauth_error

def oauth_required(view_func=None, resource_name=None):
    return CheckOAuth(view_func, resource_name)

class CheckOAuth(object):
    """
    Class that checks that the OAuth parameters passes the given test, raising
    an OAuth error otherwise. If the test is passed, the view function
    is invoked.

    We use a class here so that we can define __get__. This way, when a
    CheckOAuth object is used as a method decorator, the view function
    is properly bound to its instance.
    """
    def __init__(self, view_func, resource_name):
        self.view_func = view_func
        self.resource_name = resource_name
        update_wrapper(self, view_func)
        
    def __get__(self, obj, cls=None):
        view_func = self.view_func.__get__(obj, cls)
        return CheckOAuth(view_func, self.resource_name)
    
    def __call__(self, request, *args, **kwargs):
        if self.is_valid_request(request):
            try:
                consumer, token, parameters = self.validate_token(request)
            except OAuthError, e:
                return send_oauth_error(e)
            
            if self.resource_name and token.resource.name != self.resource_name:
                return send_oauth_error(OAuthError(_('You are not allowed to access this resource.')))
            elif consumer and token:
                return self.view_func(request, *args, **kwargs)
        
        return send_oauth_error(OAuthError(_('Invalid request parameters.')))

    @staticmethod
    def is_valid_request(request):
        # first check the HTTP Authorization header
        # - this is the preferred way to pass parameters, according to the oauth spec.
        try:
            auth_params = request.META["HTTP_AUTHORIZATION"]
        except KeyError:
            in_auth = False
        else:
            in_auth = 'oauth_consumer_key' in auth_params \
                and 'oauth_token' in auth_params \
                and 'oauth_signature_method' in auth_params \
                and 'oauth_signature' in auth_params \
                and 'oauth_timestamp' in auth_params \
                and 'oauth_nonce' in auth_params
          
        # also try the request, which covers POST and GET
        req_params = request.REQUEST
        in_req = 'oauth_consumer_key' in req_params \
            and 'oauth_token' in req_params \
            and 'oauth_signature_method' in req_params \
            and 'oauth_signature' in req_params \
            and 'oauth_timestamp' in req_params \
            and 'oauth_nonce' in req_params
        
        return in_auth or in_req

    @staticmethod
    def validate_token(request):
        oauth_server, oauth_request = initialize_server_request(request)
        return oauth_server.verify_request(oauth_request)
        
