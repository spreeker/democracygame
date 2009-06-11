"""
This module implements the Emocracy game rules as far as score keeping is
concerned. The rest of the game rules are in actions.py

this module needs to get a lot bigger..
"""

from emocracy.gamelogic.levels import change_score

VOTE_SCORE = 1
TAG_SCORE = 10
PROPOSE_SCORE = 2
PROPOSE_VOTE_SCORE = 1
ISSUE_VOTE_SCORE = 1

def vote(user, issue, new_vote, voted_already):
    """Score keeping for voting."""
    
    userprofile = user.get_profile()
    proposerprofile = issue.payload.owner.get_profile()

    if not voted_already:
        # User only gets poinst if it is the first vote on the issue.
        change_score(userprofile , VOTE_SCORE ) 
        if new_vote.vote in [-1, 1]:
            # Proposer only gets points if the issue gets a for or against vote
            # that is the first vote of the user for the Issue.
            change_score(userprofile , PROPOSE_VOTE_SCORE )
            # Issue only gets a higher score if it is the first vote that is 
            # also a for or against vote.
            issue.score += ISSUE_VOTE_SCORE 
    # Update the user's profile with his/her vote.
    if new_vote.vote == 1:
        userprofile.total_for += 1
    if new_vote.vote == -1:
        userprofile.total_against += 1
    else:
        userprofile.total_blank += 1
    # Write all that back to the database.
    issue.save()
    userprofile.save()
    proposerprofile.save()
    
def propose(user):
    """Score keeping for proposing of issues"""
    
    userprofile = user.get_profile()
    change_score(userprofile , PROPOSE_VOTE_SCORE )
    userprofile.save()

def tag(user, tag):
    """Score keeping for tagging of issues"""
    userprofile = user.get_profile()
    if not tag.points_awarded:
        change_score(userprofile , TAG_SCORE )
        userprofile.save()
    
