""""This module contains functionality that is specific to the 'original' web 
interface provided by Emocracy --- that is why this file is not in the gamelogic
app."""

def vote(request, issue, vote_int):
    """This function lets anonymous users vote, votes are stored in the session
    as key:value pairs."""
    try:
        request.session["vote_history"][issue.pk] = vote_int
    except KeyError:
        request.session["vote_history"] = {issue.pk : vote_int}
    request.session.modified = True
