"""
We want anonymous users to be able to play a litle.

This module contains functionality that is specific to the 'original' web 
interface provided by dEmocracy --- that is why this file is not in the gamelogic
app.

"""

def vote(request, issue, direction):
    """
    This function lets anonymous users vote, 
    votes are stored in the session
    as key:value pairs.i
    """
    try:
        request.session["vote_history"][issue.pk] = direction
    except KeyError:
        request.session["vote_history"] = {issue.pk : direction}
    request.session.modified = True
