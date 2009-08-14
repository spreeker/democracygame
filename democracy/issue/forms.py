from django import forms
from django.forms import ChoiceField
from django.utils.translation import ugettext as _
from issue.models import Issue, source_types
from voting.managers import votes
from tagging.forms import TagField

class IssueForm(forms.Form):
    title = forms.CharField(label=_('your issue title'), max_length = 100)
    body = forms.CharField( label=_('arguments'),
        widget = forms.Textarea(),
        max_length = 2000,
    )
    url = forms.URLField(label= _('external source of information'))
    source_type = forms.ChoiceField(label=_("source type"), choices = source_types )
    direction = forms.TypedChoiceField(label=_("your vote"), choices = votes.items(),coerce=int )

    is_draft = forms.BooleanField(label=_("publish"), initial=True, required=False)
    tags = TagField(label=_("tags"), required=True)

class Publish(forms.Form):
    is_draft = forms.TypedChoiceField(choices= ((0 , "NO"), (1, "YES")), coerce=int) 


class TagForm(forms.Form):
    tags = TagField(label=_("tags"), required=True)
