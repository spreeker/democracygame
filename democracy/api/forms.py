from django import forms
from voting.models import normal_votes
from voting.models import Issue
from issue.content.models import source_types

class IssueForm(forms.Form):
    title = forms.CharField(max_length = 100)
    body = forms.CharField(
        widget = forms.Textarea(),
        max_length = 2000,
    )
    url = forms.URLField()
    source_type = forms.CharField( widget = forms.ChoiceField( choices = source_types ))
    owners_vote = forms.ChoiceField( choices = normal_votes)

    is_draft = forms.BooleanField(initial = True, required = False)


class VoteForm(forms.Form):
    vote = forms.ChoiceField (choices = normal_votes) 
    keep_private = forms.BooleanField(initial = False , required = False )
    issue = forms.ModelChoiceField ( queryset = Issue.objects.all() )
