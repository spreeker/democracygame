from django import forms
from voting.managers import possible_votes
from issue.models import Issue
from issue.models import source_types

class IssueForm(forms.Form):
    title = forms.CharField(max_length = 100)
    body = forms.CharField(
        widget = forms.Textarea(),
        max_length = 2000,
    )
    url = forms.URLField()
    source_type = forms.CharField( widget = forms.ChoiceField( choices = source_types ))
    direction = forms.ChoiceField( choices = possible_votes)

    is_draft = forms.BooleanField(initial = True, required = False)


class VoteForm(forms.Form):
    vote = forms.ChoiceField(choices = possible_votes.items() ) 
    keep_private = forms.BooleanField(initial = False , required = False )
    issue = forms.ModelChoiceField( queryset = Issue.objects.all() )


class AuthorizeRequestTokenForm(forms.Form):
    authorize_access = forms.IntegerField(
        initial = 1,
        widget = forms.HiddenInput(attrs = {'id' : 'authorize_access'})
        )


class MultiplyForm(forms.Form):
    issue = forms.ModelChoiceField( queryset = Issue.objects.all() )
