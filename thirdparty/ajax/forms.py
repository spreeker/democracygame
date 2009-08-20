"""
Forms and validation code for ajax thirdparty stuff (mostly voting)

"""

from django import forms
from django.utils.translation import ugettext_lazy as _

normal_votes = (
    (-1 , _(u"Against")),
    (1 , _(u"For")),
)

blank_votes = [
    # content related problems with issues:
    (10, _(u'Unconvincing')),
    (11, _(u'Can\'t completely agree')),
    # form related problems with issues":
    (12, _(u"Needs more work")),
    (13, _(u"Badly worded")),
    (14,  _(u"Duplicate")),
    (15, _(u'Unrelated source')),
    # personal considerations:
    (16, _(u'I need to know more')),
    (17, _(u'Ask me later')),
]

possible_votes = list(normal_votes)
possible_votes.extend(blank_votes)
votes_to_description = dict(possible_votes)

class VoteForm(forms.Form):
    """
    Form for Voting
    
    """
    vote = forms.IntegerField(widget=forms.Select(choices = possible_votes),
                                label=_(u'vote'))
    issue = forms.IntegerField( widget = forms.HiddenInput())
#    keep_private = forms.BooleanField(required = False)
    
