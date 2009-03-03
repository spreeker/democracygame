from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext as _

class IssueCreationForm(forms.Form):
    title = forms.CharField(max_length = )
    # needs a vote
    # body title
    
#def propose(user, title, body, vote_int, source_url, source_type):
