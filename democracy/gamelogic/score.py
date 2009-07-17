"""
This module implements the Emocracy game rules as far as score keeping is
concerned. The rest of the game rules are in actions.py

this module needs to get a lot bigger..
"""

from democracy.gamelogic.levels import change_score

VOTE_SCORE = 1
TAG_SCORE = 1
PROPOSE_SCORE = 2
PROPOSE_VOTE_SCORE = 1
ISSUE_VOTE_SCORE = 1

def vote(user, issue, direction , voted_already):
    """Score keeping for voting."""
    
    userprofile = user.get_profile()
    proposerprofile = issue.user.get_profile()

    if not voted_already:
        # User only gets poinst if it is the first vote on the issue.
        change_score(userprofile , VOTE_SCORE ) 
        if direction in [-1, 1]:
            # Proposer only gets points if the issue gets a for or against vote
            change_score(proposerprofile , PROPOSE_VOTE_SCORE )
            issue.score += ISSUE_VOTE_SCORE

    # Update the user's profile with his/her vote.
    if direction == 1: userprofile.total_for += 1
    if direction == -1: userprofile.total_against += 1
    else: userprofile.total_blank += 1

    # Write all changes back to the database.
    issue.save()
    userprofile.save()
    
def propose(user):
    """Score keeping for proposing of issues"""
    
    userprofile = user.get_profile()
    change_score(userprofile , PROPOSE_SCORE )
    userprofile.save()

def tag(user, tag):
    pass

def multiply( user , issue ):
    pass


