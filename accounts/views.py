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
from emocracy_core.models import Votable
#from emocracy_core.models import Issue, Vote
import datetime

# TODO : see wether some of the custom code can be replaced with django-registration


def email_new_password(request):
    # XXX This is broken!!
    # TODO finish, make work etc (couple to mail server ?)
    # TODO see whether djan-registration is a good fit for emocracy
    return password_reset(request, 
        template_name = "accounts/email_new_password.html",
        email_template_name = "accounts/new_password_mail.html")

def create_userprofile(sender, **kwargs):
    """When a User model instance is saved this function is called to create
    a UserProfile instance if none exists already. (This function listens for
    post_save signals coming from the User model.)"""
    new_user = kwargs['instance']
    try:
        new_user.get_profile()
    except:
        new_profile = UserProfile(user = new_user, score = 0, role = 'citizen')
        new_profile.save()

post_save.connect(create_userprofile, sender = User)
    
def register_user(request):
    """User registration view."""
    if request.user.is_authenticated():
        raise Http404 # Look for a more appropriate error Http status code
    
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            new_user = User.objects.create_user(
                form.cleaned_data["username"],
                form.cleaned_data["email"], 
                form.cleaned_data["password1"])
            if request.session.has_key("vote_history"):
                migrate_votes(new_user, request.session["vote_history"])
            request.session.clear()
            user = authenticate(
                username = form.cleaned_data["username"], 
                password = form.cleaned_data["password1"]
            )
            if user is not None: # No need to check wether new user is active at all ...
                login(request, user)
            return HttpResponseRedirect(reverse('userprofile', args = [form.cleaned_data["username"]]))
    else:
        form = NewUserForm()
    
    context = RequestContext(request, {"form" : form})
    return render_to_response("accounts/register.html", context)

def migrate_votes(user, dict):
    """
    This function takes the votes in the session for an anonymous user playing
    through the web interface and upon registration copies them to the Emocracy
    database.
    """
    print dict
    userprofile = user.get_profile()
    for poll_pk, vote in dict.items():
        try:
            votable = Votable.objects.get(pk = poll_pk)
        except Votable.DoesNotExist:
            pass
        else:
            votable.vote(user, dict[poll_pk], False)
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