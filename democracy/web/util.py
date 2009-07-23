"""
Utility / helper functions for use with the web interface.
"""
import logging

from django.utils.translation import ugettext as _

from voting.models import Vote, votes_to_description

def vote_helper_anonymous(request, issues):
    """Returns a list of votes for <request.user> and the selected <issue>."""
    user_votes = []
    vote_class = []
    
    if request.session.has_key("vote_history"):
        for issue in issues:
            try:
                # Assuming there is no garbage in the user's session.  
                # (So that <request.session["vote_history"][issue.no]> will
                # always cast to an integer.)
                vote_value = int(request.session["vote_history"][issue.pk])
                try:
                    user_votes.append(votes_to_description[vote_value])
                    
                    if vote_value == -1: vote_class.append(u'against')
                    elif vote_value == 1: vote_class.append(u'for')
                    else: vote_class.append(u'blank')
                    
                except KeyError:
                    logging.info(u"NON EXISTANT VOTE INTEGER " + vote_value)
                    user_votes.append(u'KEY ERROR')
                    vote_class.append(u'blank')
            except KeyError:
                user_votes.append(_(u'I did not vote'))
                vote_class.append(u'blank')
    else:
        for issue in issues:
            user_votes.append(_(u'I did not vote'))
            vote_class.append(u'blank')
    
    return user_votes, vote_class
    

def vote_helper_authenticated(user, issues):
    """Returns a list of votes as text and css classes that go with each type of
    vote for <user> and the selected <issues>."""
    vote_text = []
    vote_class = []    
        
    for issue in issues:
        vote = Vote.objects.filter(owner = user).filter(issue = issue.pk).filter(is_archived = False)
        if vote:
            vote_value = vote[0].vote
            try:
                vote_text.append(votes_to_description[vote_value])

                if vote_value == -1: vote_class.append(u'against')
                elif vote_value == 1: vote_class.append(u'for')
                else: vote_class.append(u'blank')
                
            except KeyError:
                logging.info(u"NON EXISTANT VOTE INTEGER " + unicode(vote_value))
                vote_text.append(u'KEY ERROR')
                vote_class.append(u'blank')
        else:
            vote_text.append(_(u'I did not vote'))
            vote_class.append(u'blank')

    return vote_text, vote_class
     
def issue_sort_order_helper(request):
    """Helper function that checks the HTTP GET data and the session for the
    sort order of Issue objects in Issue list views. If it needs updating the
    session is updated with a new sort order."""
    
    order_choices = ["votes", "score", "time_stamp", "hotness"]
    default_sort_order = "time_stamp"
    try:
        sort_order = request.GET["sort_order"]
    except KeyError:
        sort_order = request.session.get("sort_order", default_sort_order)
        if not sort_order in order_choices:
            sort_order = default_sort_order        
    else:
        if not sort_order in order_choices:
            sort_order = default_sort_order
        request.session["sort_order"] = sort_order
        request.session.modified = True
    return sort_order
