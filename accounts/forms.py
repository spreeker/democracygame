from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext as _

from models import UserProfile

class NewUserForm(UserCreationForm):
    email = forms.EmailField()
    migrate_votes = forms.BooleanField(required = False)

class ChangeSettingsForm(forms.Form):
    votes_public = forms.BooleanField()
    url = forms.URLField()

class ChangeDescriptionForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('title', 'description', 'url')
    
class UserSearchForm(forms.Form):
    search_string = forms.CharField(max_length = 30, initial = _(u'Username'))