"""
This module contains the functions that implement the actions that a user can
take inside of the democracy game. Functionality in this module should not depend
on request objects. Scripts on the server, the API views and the web views 
should all call into this module to play the ddemocracy game.

This module itself uses functions from the score.py and levels.py see if
an action is allowed and how it affects the score of the players / the democracy
world.

user_action = get_actions( user )

user role_to_actions to determine permission and availability of actions

vote_func = role_to_actions[userprofile.role]['vote'] this will return the function required to do the 
vote for this user. If it returns a keyerror the action for this user does not excist.

"""

import logging
import datetime

from django.utils.translation import ugettext as _
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

import score
import levels
from democracy.gamelogic.models import roles

from gamelogic.models import tag_count_threshold
from gamelogic.models import MultiplyIssue
from voting.models import Vote
from voting.models import Issue
from voting.models import votes_to_description
from issue_content.models import IssueBody


def vote(user, issue, vote_int, keep_private , api_interface=None ):
    """Unified voting (both blank and normal votes)."""
    userprofile = user.get_profile()
    if not role_to_actions[userprofile.role].has_key('vote') : return

    voted_already, repeated_vote = archive_votes( user, issue , vote_int)
    if repeated_vote: return
    
    new_vote = Vote( owner = user, issue = issue, vote = vote_int, keep_private = keep_private)
    new_vote.save()

    logging.debug("User " + user.username + " voted " + unicode(new_vote.vote) + " on issue object with pk =" + unicode(issue.id) + ".")
    
    score.vote(user, issue, new_vote, voted_already)
    levels.upgrade[userprofile.role](userprofile)
    user.message_set.create(message="You voted successfully on %s" % issue.title  )

    return new_vote

def archive_votes(user, issue,  vote_int):
    """archive old votes by switching the is_archived flag to True
    for all the previous votes on <issue> by <user>.
    And we check for and dismiss a repeated vote.
    """
    votes = Vote.objects.filter(owner = user, is_archived = False, issue = issue)
    voted_already = False
    repeated_vote = False
    for v in votes:
        if vote_int == v.vote: #check if you do the same vote again.
            repeated_vote = True
        else:
            v.is_archived = True
            v.save()
        voted_already = True
    return voted_already, repeated_vote

def propose(user, title, body, vote_int, source_url, source_type, is_draft = False, issue_no = None):
    """ Propose an issue into the game
    """
    if issue_no == None:
        userprofile = user.get_profile()
        if not role_to_actions[userprofile.role].has_key('propose'): return 

        # user may not have another issue with the same title
        try :
            Issue.objects.get( title = title , owner = user )
            return " trying to create the same issue"
        except Issue.DoesNotExist :
            pass 

        new_issue = IssueBody.objects.create(
            owner = user,
            title = title,
            body = body,
            url = source_url,
            source_type = source_type,
            time_stamp = datetime.datetime.now(),
        )
        
        new_issue = Issue.objects.create_for_object(new_issue, title = new_issue.title, owner = user, is_draft = is_draft)
        new_issue.vote(user, vote_int, keep_private = False)    

        user.message_set.create(message="You created issue \"%s\" successfully " % new_issue.title  )

        score.propose(user)
        levels.upgrade[userprofile.role](userprofile)

    else: # we are editing one TODO remove this possibility?
        # Grab the existing issue from db.
        issue = get_object_or_404(Issue, pk = issue_no)
        # If an old vote exists, remove it and perform a new vote.
        try:
            # TODO
            # If users were to be allowed to change their opinion on their own
            # issue the following line needs to use a filter() instead of get().
            owners_vote = Vote.objects.get(issue = issue, owner = user)
            owners_vote.delete()
        except Vote.DoesNotExist:
            pass
        issue.vote(user, vote_int, keep_private = False)
        # Now change the issue and issue body to the appropriate values.
        issue.title = title
        issue.time_stamp = datetime.datetime.now()
        issue.is_draft = is_draft
        
        issue.payload.title = title
        issue.payload.body = body
        issue.payload.time_stamp = datetime.datetime.now()
        issue.payload.source_type = source_type
        issue.payload.source_url = source_url
        
        issue.payload.save()
        issue.save()
        new_issue = issue

    return new_issue

def tag(user, issue, tag_string):
    # The idea behind tagging in democracy:
    # User tags something, tag will only show up if it is already used a certain
    # number of times throughout Emocracy. Only then will points be
    # awarded for that tag and only for the first user to use the tag.
    # As an aside I see 2 problems with that:
    # 1 - a user can himself tag a bunch of different issues with the same tag
    # and thereby give himself points put and garbage in the database (if that
    # is what he wanted). Possible work around : make tagging take points. Make
    # it more expensive to tag randomly like described above compared to the
    # poinst scored through a tag showing up in democracy.
    # 2 - Registering all tags you can think of to get points the moment they
    # start seeing use. (Like domain squatters with domain names ... ) A work
    # around that problem would also make tagging cost points somehow ...
    
    tag, first_time = issue.tag(user, tag_string)
    
    if tag.count > tag_count_threshold:
        # Make tag visible if it is used more than a minimun number of times
        # on any issue.
        if tag.count > tag_count_threshold:
            tag.visible = True
        
        if not tag.points_awarded:
            score.tag(user, tag)
            tag.points_awarded = True
    tag.save()
    
    return tag, _(u'Tag %(tagname)s added to this issue. The new tag might not show up immediately' % {'tagname' : tag.name})

def multiply(user , issue , downgrade = False ):
    """
    Opinion leaders have the option to mutiply the values of issues. 
    at most X multyplies can be given.

    check if there are multipliers left.
    add multiplier to issue.but not your own.

    checks are done at model level.
    """
    userprofile = user.get_profile()
    if not role_to_actions[userprofile.role].has_key('multiply'): return 

    m = MultiplyIssue.objects.create( owner = user , issue = issue , downgrade = downgrade )
    # TODO score change?
    return m.save()


role_to_actions = {
    'anonymous citizen' : {
        'vote' : vote,
    },
    'citizen' : {
        'vote' : vote,
        'tag' : tag,
    },
    'active citizen' : {
        'vote' : vote,
        'tag' : tag,
        'propose' : propose,
    },
    'opinion leader' : {
        'vote' : vote,
        'tag' : tag,
        'propose' : propose,
        'multiply' : multiply,
    }
}


def do( user , action , *args , **kwargs ):
    """ We will look up the role of a user
        Then Lookup if we can do the actions
        execute the action and return the result

        return False if actions failed
    """
    try :
        role = user.get_profile().role
        action = role_to_actions[role][action]
    except KeyError :
        logging.debug( "user %s does not have permisson to do %s " % ( user , action ))
        return
    except ObjectDoesNotExist :
        logging.debug( " user %s does not have an profile BIG FAT ERROR " % ( user ))
        raise

    return action( user , *args , **kwargs )


def get_actions(user):
    """ return all possible game actions for a user """
    if not user.is_authenticated()  : return role_to_actions['anonymous citizen']
    userprofile = user.get_profile()
    actions = role_to_actions[userprofile.role]
    return actions

def get_unavailable_actions(user = None):
    """ return dict with all gameactions a user cannot do with the
        required role as value
    """
    if not user.is_authenticated(): userprofile = {}
    else : userprofile = user.get_profile()

    all_actions = {}
    
    for role in roles: 
        actions = role_to_actions.get(role , {} )
        for action , function in actions.iteritems():
            all_actions.setdefault( action , role )
    for action , function in get_actions(user).iteritems():
        all_actions.pop(action)

    return all_actions
