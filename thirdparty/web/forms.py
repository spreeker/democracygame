
from django.utils.translation import ugettext as _
from django import forms

normal_votes = (
    (-1 , _(u"Against")),
    (1 , _(u"For")),
)

source_types = (
    (u"website", _(u"website")),
    (u"video", _(u"video")),
    (u"audio", _(u"audio")),
    (u"book", _(u"book")),
    (u"document", _(u"document")),
    (u"image", _(u"image")),
)


class IssueFormNew(forms.Form):
    title = forms.CharField(max_length = 100)
    body = forms.CharField(
        widget = forms.Textarea(),
        max_length = 2000,
    )
    url = forms.URLField()
    source_type = forms.CharField(
        widget = forms.Select(choices = source_types)
    )
    owners_vote = forms.IntegerField(widget = forms.Select(
        choices = normal_votes,
    ))
    is_draft = forms.BooleanField(initial = True, required = False)

