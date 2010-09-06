from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext as _

from models import UserProfile

from registration.forms import RegistrationFormTermsOfService
from registration.forms import RegistrationFormUniqueEmail

class ChangeSettingsForm(forms.Form):
    votes_public = forms.BooleanField()
    url = forms.URLField()

class ChangeDescriptionForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('title', 'description', 'url')
    
class UserSearchForm(forms.Form):
    search_string = forms.CharField(max_length = 30, initial = _(u'Username'))

class RegistrationTermsOfServiceUniqueEmail(
        RegistrationFormUniqueEmail
        ):
        """
        Subclass of RegistrationForms which enforces
        an unique email.
        """


class ChangeProfile(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('title', 'description', 'url', 
                   'id_is_verified', 'votes_public', 'show_identity' )
        
