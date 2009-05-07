# By Thijs Coenen for the Emocracy project.

"""
This module contains the functions that implement the actions that a user can
take inside of the emocracy game. Functionality in this module should not depend
on request objects. Scripts on the server, the API views and the web views 
should all call into this module to play the emocracy game.

This module itself uses functions from the allow.py and score.py to see wether 
an action is allowed and how it affects the score of the players / the emocracy
world.
"""

import logging
import datetime

from django.utils.translation import ugettext as _
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User

from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType


import allow
import score
from models import Mandate, tag_count_threshold
from voting.models import Vote
from voting.models import Vote, Issue
from voting.models import votes_to_description
from issues.models import IssueBody



# -- Authenticated voting: -----------------------------------------------------

def vote(user, issue, vote_int, keep_private):
    """Unified voting (both blank and normal votes)."""
    logging.info(u"actions.vote called")
    # TODO reenable the check on whether the action is allowed
    #if not allow.vote(user, issue, vote_int, keep_private): return
    voted_already, repeated_vote = archive_votes(issue, user, vote_int)
    if repeated_vote: return
    # TODO make this use the appropriate instance method of the Issue object
    new_vote = Vote(
        owner = user,
        issue = issue,
        time_stamp = datetime.datetime.now(),
        vote = vote_int,
        keep_private = keep_private
    )
    new_vote.save()
    logging.info(u"User " + user.username + u" voted " + unicode(new_vote.vote) + u" on issue object with pk =" + unicode(issue.id) + ".")
    
    score.vote(user, issue, new_vote, voted_already)

    return new_vote

def archive_votes(issue, user, vote_int):
    """This function archives old votes by switching the is_archived flag to True
    for all the previous votes on <issue> by <user>."""
    
    # TODO : clean up this function and its interaction with the voting 
    # functions. See wether it should be a manager function in models.py!
    votes = Vote.objects.filter(owner = user, is_archived = False, issue = issue)
    voted_already = False
    repeated_vote = False
    for v in votes:
        if vote_int == v.vote:
            repeated_vote = True
        else:
            v.is_archived = True
            v.save()
        voted_already = True
    return voted_already, repeated_vote

def propose(user, title, body, vote_int, source_url, source_type):
    if not allow.propose(user, title, body, vote_int, source_url, source_type): return None

    new_issue = IssueBody.objects.create(
        owner = user,
        title = title,
        body = body,
        url = source_url,
        source_type = source_type,
        time_stamp = datetime.datetime.now(),
    )
    
    new_issue = Issue.objects.create_for_object(new_issue, title = new_issue.title, owner = user)
    new_issue.vote(user, vote_int, keep_private = False)    

    score.propose(user)
    return new_issue

def tag(user, issue, tag_string):
    if not allow.tag(user, issue, tag_string): return
    # TODO look into manual transaction control (either do everything below and
    # commit or fail to do any of it).
    
    # The idea behind tagging in emocracy:
    # User tags something, tag will only show up if it is already used a certain
    # number of times throughout Emocracy. Only then will points be
    # awarded for that tag and only for the first user to use the tag.
    # As an aside I see 2 problems with that:
    # 1 - a user can himself tag a bunch of different issues with the same tag
    # and thereby give himself points put and garbage in the database (if that
    # is what he wanted). Possible work around : make tagging take points. Make
    # it more expensive to tag randomly like described above compared to the
    # poinst scored through a tag showing up in emocracy.
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

def mandate(user, representative):
    if not allow.mandate(user, representative): return
    try:
        m = Mandate.objects.get(user = user)
        m.representative = representative
        m.save()
    except ObjectDoesNotExist:
        m = Mandate(user = user, representative = representative)
        m.save()
    except:
        raise
    
def become_candidate(user):
    if not allow.become_candidate(user): return
    return
    # make total profile public (minus real life info)
