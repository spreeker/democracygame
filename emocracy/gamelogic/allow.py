"""
This module implements part of the Emocracy game rules. Here the checks on
wether some action is allowed for a certain user are implented.
The rest of the game rules are in score.py and allow.py .
"""
# TODO : check how user.is_authenticated() calls are to be handled when the
# user is not logged in through the normal django.auth web stuff (aka: how does
# one deal with API users ...)

def vote(user, issue, vote_int, keep_private):
    if user.is_authenticated():
        return True
    return False

def propose(user, title, body, vote_int, source_url, source_type):
    if user.is_authenticated():
        return True
    return False

def tag(user, votable, tag):
    if user.is_authenticated():
        return True
    return False

def mandate(user, representative):
    if user.is_authenticated() and user != representative:
        return True
    return False

def become_candidate(user):
    if user.is_authenticated():
        return True
    return False