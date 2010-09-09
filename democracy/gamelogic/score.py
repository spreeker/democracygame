"""
This module implements the Emocracy game rules as far as score keeping is
concerned. The rest of the game rules are in actions.py

this module needs to get a lot bigger..
"""

from gamelogic.levels import change_score

VOTE_SCORE = 1
USER_VOTE_SCORE = 20
TAG_SCORE = 1
PROPOSE_SCORE = 2
PROPOSE_VOTE_SCORE = 1
ISSUE_VOTE_SCORE = 1

def vote(user, issue, direction , voted_already):
    """Score keeping for voting."""
    
    if not voted_already:
        # User only gets poinst if it is the first vote on the issue.
        change_score(user , VOTE_SCORE ) 
        if direction in [-1, 1]:
            # Proposer only gets points if the issue gets a for or against vote
            change_score(issue.user , PROPOSE_VOTE_SCORE )
            issue.score += ISSUE_VOTE_SCORE

    # Write all changes back to the database.
    issue.save()
    
def vote_user(user, voted_user, direction, voted_already):
    """score keeping for voting on an other user
    """
    if not voted_already:
       # User only gets points if user is the first vote.
       change_score(voted_user, USER_VOTE_SCORE)
       change_score(user, USER_VOTE_SCORE) 
    change_score(voted_user, 0) #check parelement score voted_user

def propose(user):
    """Score keeping for proposing of issues"""
    change_score(user, PROPOSE_SCORE)

def tag(user, tag):
    pass

def multiply(user, issue):
    pass


