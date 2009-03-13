"""
This module contains Django forms.Form definitions that are used to validate the
incoming post data sent to the API. By reusing the forms from Django it is not
necessary to build some custom post data validation.
"""

from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext as _
from gamelogic.models import source_types, possible_votes, normal_votes

class IssueCollectionForm(forms.Form):
    # TODO : see wether this can done more cleanly (as there is some duplication
    # of information the gamelogic/models.py module).
    title = forms.CharField(max_length = 200)
    body = forms.CharField(max_length = 2000, widget = forms.Textarea())
    vote_int = forms.IntegerField()
    source_url = forms.URLField(verify_exists = False)
    source_type = forms.ChoiceField(choices = source_types)
    
    def clean_vote_int(self):
        """Verify that we are dealing with a valid for or against vote. """
        allowed_values = [x[0] for x in normal_votes]
        data = self.cleaned_data['vote_int']
        if not data in allowed_values:
            raise forms.ValidationError('vote_int not valid')
        return data
        
    
    
