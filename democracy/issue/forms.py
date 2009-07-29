from django import forms
from django.forms import ChoiceField
from issue.models import Issue, source_types
from voting.managers import votes
from django.utils.translation import ugettext as _

class IssueForm(forms.Form):
    title = forms.CharField(label=_('your issue'), max_length = 100)
    body = forms.CharField( label=_('arguments'),
        widget = forms.Textarea(),
        max_length = 2000,
    )
    url = forms.URLField(label= _('external source for extra information'))
    source_type = forms.ChoiceField(label=_("source type"), choices = source_types )
    direction = forms.TypedChoiceField(label=_("your vote"), choices = votes.items(),coerce=int )

    is_draft = forms.BooleanField(label=_("publish"), initial=True, required=False)

class Publish(forms.Form):
    is_draft = forms.BooleanField()

