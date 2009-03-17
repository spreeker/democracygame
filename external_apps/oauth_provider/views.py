from oauth.oauth import OAuthError

from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import get_callable

from utils import initialize_server_request, send_oauth_error
from decorators import oauth_required

OAUTH_AUTHORIZE_VIEW = 'OAUTH_AUTHORIZE_VIEW'
OAUTH_CALLBACK_VIEW = 'OAUTH_CALLBACK_VIEW'
INVALID_PARAMS_RESPONSE = send_oauth_error(OAuthError(
                                            _('Invalid request parameters.')))

def request_token(request):
    """
    The Consumer obtains an unauthorized Request Token by asking the Service 
    Provider to issue a Token. The Request Token's sole purpose is to receive 
    User approval and can only be used to obtain an Access Token.
    """
    oauth_server, oauth_request = initialize_server_request(request)
    if oauth_server is None:
        return INVALID_PARAMS_RESPONSE
    try:
        # create a request token
        token = oauth_server.fetch_request_token(oauth_request)
        # return the token
        response = HttpResponse(token.to_string(), mimetype="text/plain")
    except OAuthError, err:
        response = send_oauth_error(err)
    return response
    
@login_required
def user_authorization(request):
    """
    The Consumer cannot use the Request Token until it has been authorized by 
    the User.
    """
    oauth_server, oauth_request = initialize_server_request(request)
    if oauth_request is None:
        return INVALID_PARAMS_RESPONSE
    try:
        # get the request token
        token = oauth_server.fetch_request_token(oauth_request)
    except OAuthError, err:
        return send_oauth_error(err)

    try:
        # get the request callback, though there might not be one
        callback = oauth_server.get_callback(oauth_request)
    except OAuthError:
        callback = None

    # entry point for the user
    if request.method == 'GET':
        # try to get custom authorize view
        authorize_view_str = getattr(settings, OAUTH_AUTHORIZE_VIEW, 
                                    'oauth_provider.views.fake_authorize_view')
        try:
            authorize_view = get_callable(authorize_view_str)
        except AttributeError:
            raise Exception, "%s view doesn't exist." % authorize_view_str
        params = oauth_request.get_normalized_parameters()
        # set the oauth flag
        request.session['oauth'] = token.key
        return authorize_view(request, token, callback, params)
    
    # user grant access to the service
    elif request.method == 'POST':
        # verify the oauth flag set in previous GET
        if request.session.get('oauth', '') == token.key:
            request.session['oauth'] = ''
            try:
                if int(request.POST['authorize_access']):
                    # authorize the token
                    token = oauth_server.authorize_token(token, request.user)
                    # return the token key
                    args = token.to_string(only_key=True)
                else:
                    args = 'error=%s' % _('Access not granted by user.')
            except OAuthError, err:
                response = send_oauth_error(err)
            if callback:
                if "?" in callback:
                    url_delimiter = "&"
                else:
                    url_delimiter = "?"
                response = HttpResponseRedirect('%s%s%s' % (callback, url_delimiter, args))
            else:
                # try to get custom callback view
                callback_view_str = getattr(settings, OAUTH_CALLBACK_VIEW, 
                                    'oauth_provider.views.fake_callback_view')
                try:
                    callback_view = get_callable(callback_view_str)
                except AttributeError:
                    raise Exception, "%s view doesn't exist." % callback_view_str
                response = callback_view(request)
        else:
            response = send_oauth_error(OAuthError(_('Action not allowed.')))
        return response
    
def access_token(request):
    """
    The Consumer exchanges the Request Token for an Access Token capable of 
    accessing the Protected Resources.
    """
    oauth_server, oauth_request = initialize_server_request(request)
    if oauth_request is None:
        return INVALID_PARAMS_RESPONSE
    try:
        # get the request token
        token = oauth_server.fetch_access_token(oauth_request)
        # return the token
        response = HttpResponse(token.to_string(), mimetype="text/plain")
    except OAuthError, err:
        response = send_oauth_error(err)
    return response

@oauth_required
def protected_resource_example(request):
    """
    Test view for accessing a Protected Resource.
    """
    return HttpResponse('Protected Resource access!')

@login_required
def fake_authorize_view(request, token, callback, params):
    """
    Fake view for tests. It must return an ``HttpResponse``.
    
    You need to define your own in ``settings.OAUTH_AUTHORIZE_VIEW``.
    """
    return HttpResponse('Fake authorize view for %s.' % token.consumer.name)

def fake_callback_view(request):
    """
    Fake view for tests. It must return an ``HttpResponse``.
    
    You can define your own in ``settings.OAUTH_CALLBACK_VIEW``.
    """
    return HttpResponse('Fake callback view.')
