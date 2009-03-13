# by Thijs Coenen for the Emocracy project october 2008
from emocracy.gamelogic.models import blank_votes, blank_votes, Tag, source_types, normal_votes

from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext as _

possible_motivations = [x[0] for x in blank_votes]

class HiddenOkForm(forms.Form):
    ok = forms.BooleanField(initial = True, widget = forms.HiddenInput())

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

class TagForm(forms.Form):
    tags = forms.CharField(max_length = 50)
    issue_no = forms.IntegerField(widget = forms.HiddenInput())

def tag_selection_helper():
    qs = Tag.objects.get_popular(10)
    l = [(u'', u'--------')]
    l.extend([(unicode(x), unicode(x)) for x in qs]) # TODO make HTML safe! XXX
    return l

class TagForm2(forms.Form):
    """Form used by the Javascript less version of the tagging system."""
    
    tags = forms.CharField(max_length = 50, required = False)
    def __init__(self, *args, **kwargs):
        """Initializes form instances, is needed to be able to set the popular
        tags field dynamically (on a per instance basis)."""
        super(TagForm2, self).__init__(*args, **kwargs)
        self.fields['popular_tags'] = forms.ChoiceField(choices = tag_selection_helper(), required=False)
    
    def clean(self):
        cleaned_data = self.cleaned_data
        if not cleaned_data['tags'] and not cleaned_data['popular_tags']:
            raise forms.ValidationError(u'No tag selected or given.')            
        else:
            return cleaned_data

class TagSearchForm(forms.Form):
    search_string = forms.CharField(max_length = 50, initial = _(u'Tag'))

class NormalVoteForm(forms.Form):
    vote = forms.IntegerField(widget = forms.Select(
        choices = [(u"-1", _(u"Against")), (u"0", _(u"Blank...")), (u"1", _(u"For"))]
    ))
    keep_private = forms.BooleanField(required = False, initial = False)

class BlankVoteForm(forms.Form):
    motivation = forms.IntegerField(widget = forms.Select(
        choices = blank_votes
    ))
    keep_private = forms.BooleanField(required = False, initial = False)

class CastVoteFormFull(forms.Form):
    """
    Full vote form. (Allows both motivated blank votes or unmotivated 'for' or 
    'against' votes.)
    """
    vote = forms.IntegerField(widget = forms.Select(
        choices = [(u"-1", _(u"Against")), (u"0", _(u"Blank...")), (u"1", _(u"For"))]
    ))
    motivation = forms.IntegerField(widget = forms.Select(
        choices = blank_votes
    ))
    issue_no = forms.IntegerField(widget = forms.HiddenInput())
    keep_private = forms.BooleanField(required = False)
    # second_step is used for non AJAX submissions (to show or not show certain
    # fields)
    second_step = forms.BooleanField(required = False, initial = False, widget = forms.HiddenInput())
    
    
    def clean(self):
        """
        Protect against garbage form data. This function checks that: 
        -blank votes are motivated
        -the votes are either for, against or blank
        This function also sets the motivation of a 'for' or 'against' vote
        to an empty string and defaults the keep_private variable to False if
        it is not available.
        """
                
        cleaned_data = self.cleaned_data
                
        try:
            vote_int = cleaned_data['vote']
        except KeyError:
            #print 'No vote'
            raise forms.ValidationError(u'No vote')

        if not vote_int in [-1, 0, 1]:
            #print u'Invalid vote'
            raise forms.ValidationError(u'Invalid vote')
        
        try:
            issue_no = cleaned_data['issue_no']
        except KeyError:
            #print 'No issue'
            raise forms.ValidationError(u'No issue')
        
        try:
            motivation = cleaned_data['motivation']
        except KeyError:
            motivation = None

        if vote_int == 0:
            if motivation not in possible_motivations:
                #print 'Invalid motivation'
                raise forms.ValidationError(u'Invalid motivation')
        else: 
            # We already know vote_int to be in [-1, 0, 1] so here we have 
            # vote_int in [-1, 1] -> obliterate the motivation.
            # TODO check wether this is a redundant check.
            cleaned_data[u'motivation'] = 0
        
        try:
            keep_private = cleaned_data[u'keep_private']
        except KeyError:
            #print "keep_private reset"
            cleaned_data[u'keep_private'] = False

        return cleaned_data
