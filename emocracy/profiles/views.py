from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404
from django.db.models.signals import post_save
from django.http import HttpResponseRedirect
from django.contrib.auth.views import password_reset
from django.utils.translation import ugettext as _
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.core.urlresolvers import reverse

from forms import NewUserForm, ChangeSettingsForm, ChangeDescriptionForm, UserSearchForm
from django.contrib.auth.forms import PasswordResetForm
from models import UserProfile
from gamelogic.models import Issue

#imports for activate view
from registration.models import RegistrationProfile
from django.conf import settings

import datetime

# TODO : see wether some of the custom code can be replaced with django-registration

def create_userprofile(sender, **kwargs):
    """
    When a User model instance is saved this function is called to create
    a UserProfile instance if none exists already. (This function listens for
    post_save signals coming from the User model.)
    If you create a user anywhere , in the admin or
    official registration way , this code will make sure there is a userprofile. 
    """
    new_user = kwargs['instance']
    try:
        new_user.get_profile()
    except:
        new_profile = UserProfile(user = new_user, score = 0, role = 'citizen')
        new_profile.save()

post_save.connect(create_userprofile, sender = User)

def activate(request, activation_key,
             template_name='registration/activate.html',
             extra_context=None):
    """
    THIS COMES FROM EXTERNAL APPS REGISTRATION.
    modifications will be marked with a line like below.    
    we need modification to make saving annonymous votes possible
    to a new profile.
    =================================================================
    Activate a ``User``'s account from an activation key, if their key
    is valid and hasn't expired.
    
    By default, use the template ``registration/activate.html``; to
    change this, pass the name of a template as the keyword argument
    ``template_name``.
    
    **Required arguments**
    
    ``activation_key``
       The activation key to validate and use for activating the
       ``User``.
    
    **Optional arguments**
       
    ``extra_context``
        A dictionary of variables to add to the template context. Any
        callable object in this dictionary will be called to produce
        the end result which appears in the context.
    
    ``template_name``
        A custom template to use.
    
    **Context:**
    
    ``account``
        The ``User`` object corresponding to the account, if the
        activation was successful. ``False`` if the activation was not
        successful.
    
    ``expiration_days``
        The number of days for which activation keys stay valid after
        registration.
    
    Any extra variables supplied in the ``extra_context`` argument
    (see above).
    
    **Template:**
    
    registration/activate.html or ``template_name`` keyword argument.
    
    """
    activation_key = activation_key.lower() # Normalize before trying anything with it.
    account = RegistrationProfile.objects.activate_user(activation_key)
    if extra_context is None:
        extra_context = {}
    context = RequestContext(request)
    #====================================================
    # custom emocracy code below
    #====================================================
    session_votes = False
    if request.session.has_key("vote_history"):
        session_votes = True    
        if account: 
            migrate_votes(account, request.session["vote_history"])

    extra_context.update( { 'votes_saved' : session_votes } )

    #=========================================================
    # end custom code
    #========================================================
    for key, value in extra_context.items():
        context[key] = callable(value) and value() or value
    return render_to_response(template_name,
                              { 'account': account,
                                'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS },
                              context_instance=context)

def migrate_votes(user, dict):
    """
    This function takes the votes in the session for an anonymous user playing
    through the web interface and upon registration copies them to the Emocracy
    database.
    """
    userprofile = user.get_profile()
    for poll_pk, vote in dict.items():
        try:
            issue = Issue.objects.get(pk = poll_pk)
        except Issue.DoesNotExist:
            pass
        else:
            issue.vote(user, dict[poll_pk], False)
            if vote == 1:
                userprofile.total_for += 1
            elif vote == -1:
                userprofile.total_against += 1
    userprofile.save()

def userprofile_show(request, username):
    user = get_object_or_404(User, username = username) 
    context = RequestContext(request, {
        'user_to_show' : user,
        'profile' : user.get_profile(),
    })
    if user == request.user:
        return render_to_response('accounts/self_detail.html', context)
    else:
        return render_to_response('accounts/user_detail.html', context)

@login_required
def change_description(request):
    p = request.user.get_profile()
    if request.method == 'POST':
        form = ChangeDescriptionForm(request.POST)
        if form.is_valid():
            p.title = form.cleaned_data['title']
            p.description = form.cleaned_data['description']
            p.url = form.cleaned_data['url']
            p.save()
            return HttpResponseRedirect(reverse('userprofile', args = [request.user.username]))
    else:
        form = ChangeDescriptionForm(instance = p)
    context = RequestContext(request, {
        'form' : form,        
    })
    return render_to_response('accounts/change_description.html', context)

def search_user(request):
    """This view let's users search for other users by username..."""
    # TODO : fix unicode in request parameters.
    # (Conrado says it is not allowed, google does it anyway ...)
    # TODO FIXME XSS handle the way the search_string shows up in the page -
    # since that is not handled cleanly/correctly at the moment.
    if request.method == 'POST':
        form = UserSearchForm(request.POST)
        if form.is_valid():
            search_string = form.cleaned_data["search_string"]
        else:
            search_string = u''
    else:
        form = UserSearchForm()
        search_string = request.GET.get(u'search_string', u'')

    if not search_string == u'':
        qs = User.objects.filter(username__icontains = search_string)
    else:
        qs = User.objects.none()
    
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
    return render_to_response('accounts/search_user.html', context)
