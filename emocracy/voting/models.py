"""This is the core of the Emocracy voting system. The Issue model in this 
module can be generically linked to anything that users whould be able to vote
on.

This module implements:
-voting database interactions
-tagging database interactions

Note that the game rules should not be added to this module.
"""

import datetime

from django.db import models, IntegrityError
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext as _


# ADD NEW POSSIBILITIES WITH NEW INTEGERS, THEY NEED TO BE UNIQUE
# LEAVE OLD ENTRIES SO AS NOT TO MESS THE DATABASE UP!

normal_votes = (
    (-1 , _(u"Against")),
    (1 , _(u"For")),
)

blank_votes = [
    # content related problems with issues:
    (10, _(u'Unconvincing')),
    (11, _(u'Can\'t completely agree')),
    # form related problems with issues":
    (12, _(u"Needs more work")),
    (13, _(u"Badly worded")),
    (14,  _(u"Duplicate")),
    (15, _(u'Unrelated source')),
    # personal considerations:
    (16, _(u'I need to know more')),
    (17, _(u'Ask me later')),
]

possible_votes = list(normal_votes)
possible_votes.extend(blank_votes)
votes_to_description = dict(possible_votes)

class IssueManager(models.Manager):
    def get_for_object(self, obj):
        # TODO add check: is obj a Django Model and does it have ContentType entry
        ctype = ContentType.objects.get_for_model(obj)
        return self.filter(content_type = ctype.pk,
            object_id = obj.pk)

    def create_for_object(self, obj, *args, **kwargs):
        # TODO add check: is obj a Django Model and does it have ContentType entry
        # TODO enforce uniqueness (either through Django or something homebrew)
        title = kwargs.pop('title', '')
        owner = kwargs.pop('owner', None)
        new_issue = self.create(
            owner = owner,
            title = title,
            time_stamp = datetime.datetime.now(),
            payload = obj,
        )        
        return new_issue

class Issue(models.Model):
    """
    voting issue. 
    
    # create an issue. 
    >>> from issues_content.models import IssueBody
    >>> tuser = User.objects.create_user('john', 'john@john.com', 'pass')
    >>> tissue = IssueBody.objects.create( owner = tuser, title = 'tissue',body = 'body',url = 'tissue.org',source_type = 'website', time_stamp = datetime.datetime.now())
    >>> tissue = Issue.objects.create_for_object(tissue, title=tissue.title, owner=tissue.owner)
    >>> tissue.vote(tuser, -1, False)
    <Vote: -1 on "tissue" by john>

    """
    owner = models.ForeignKey(User)
    title = models.CharField(blank = True, max_length = 200)
    time_stamp = models.DateTimeField()
    
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField() # or just a IntegerField -> TODO find out!
    payload = generic.GenericForeignKey('content_type', 'object_id')
    
    # Denormalized data - for sort order and to give the DB a break ;)
    offensiveness = models.IntegerField(default = 0)
    score = models.IntegerField(default = 0)
    votes = models.IntegerField(default = 0)
    hotness = models.IntegerField(default = 0)
    # TODO add a denomalized count of anonymous votes.
    
    objects = IssueManager()
    
    class Meta:
        unique_together = ('content_type', 'object_id') # UNIQUENESS CONSTRAINT SEEMS TO BE IGNORED? FIXME

    def vote(self, user, vote_int, keep_private, issueset = None):
        new_vote = Vote.objects.create(
            owner = user,
            issue = self,
            issueset = issueset,
            vote = vote_int,
            keep_private = keep_private,
            time_stamp = datetime.datetime.now()
        )
        self.votes += 1 # See how this interacts with Emocracy design TODO
        self.save()
        return new_vote
        
    def anonymous_vote():
        # TODO needs to register an anonymous vote in the anonymous vote table.
        pass
    
    def tag(self, user, tag_string):
        # Get the tag object and if it does not exist yet, create it.
        try:
            tag = Tag.objects.get(name = tag_string)
            tag.count += 1
        except Tag.DoesNotExist:
            tag = Tag.objects.create(
                name = tag_string,
                first_suggested_by = user,
                count = 1
            )
        # Make tag visible if it is used enough times.
        tag.save()
        # Find out wether the user has tagged this issue already with this tag.
        try:
            ti = TaggedIssue.objects.create(
                issue = self,
                tag = tag,
                user = user
            )
            first_time = True
        except IntegrityError:
            first_time = False
        return tag, first_time
            
            
class IssueSet(models.Model):
    owner = models.ForeignKey(User)
    title = models.CharField(max_length = 200)
    body = models.TextField(max_length = 2000)
    time_stamp = models.DateTimeField()
    issues = models.ManyToManyField(Issue) # add a trough keyword later ...
    users = models.ManyToManyField(User, related_name = 'pollusers')
    
    def __unicode__(self):
        return self.title
        
# ------------------------------------------------------------------------------
# Vote Models:
#
# If api_interface is blank/null that means vote came in through the Emocracy 
# web interface.

class Vote(models.Model):
    api_interface = models.CharField(max_length = 50, blank = True)
    owner = models.ForeignKey(User)
    
    issue = models.ForeignKey(Issue)
    issueset = models.ForeignKey(IssueSet, null = True)
    vote = models.IntegerField(choices = possible_votes)
    time_stamp = models.DateTimeField(editable = False)
    is_archived = models.BooleanField(default = False)
    keep_private = models.BooleanField(default = False)
    
    def __unicode__(self):
        return unicode(self.vote) + u" on \"" + self.issue.title + u"\" by " + self.owner.username

class AnonymousVote(models.Model):
    api_interface = models.CharField(max_length = 50, blank = True)
    session_id = models.CharField(max_length = 32) # Django session identifiers have

    issue = models.ForeignKey(Issue)
    issueset = models.ForeignKey(IssueSet, null = True)
    vote = models.IntegerField(choices = possible_votes)
    time_stamp = models.DateTimeField(editable = False)

# ------------------------------------------------------------------------------
# -- Bare bones Tagging implementation -----------------------------------------

# Rationale: Django-tagging does not keep counts of the number of tags for an
# model. I need that number because a new tag should only show up after
# a certain number of users have used it (on any Issue, so Model wide counts
# will suffice). On the other hand the only things that can be tagged in
# Emocracy are Issues/stuff you can vote on - so there is no need to user the
# generic foreign key facilities in Django

# TODO look at the way the Tag objects are found, see wether that
# can be done more cleanly (/better /faster). Probably through some 
# custom SQL ...
# Possible way to speed up get_for_issue: have a TagField on an Issue
# (that would get rid of the TaggedIssue query).


class TagManager(models.Manager):
    def get_for_issue(self, issue, max_num = 10):        
        tag_ids = TaggedIssue.objects.filter(issue = issue).values_list('tag', flat = True)
        return self.filter(pk__in = tag_ids).filter(visible = True).distinct().order_by('count').reverse()[:max_num]
    def get_popular(self, max_num = 10):
        return self.all().order_by('count').reverse()[:max_num]
        

class Tag(models.Model):
    """This is a tag, a """
    name = models.CharField(max_length = 50, unique = True)
    first_suggested_by = models.ForeignKey(User, null = True)
    points_awarded = models.BooleanField(default = False)
    visible = models.BooleanField(default = False)
    count = models.IntegerField(default = 0) # denormalized ... 
    objects = TagManager()
    
    def __unicode__(self):
        return self.name
    
    def get_issues(self):
        issue_ids = TaggedIssue.objects.filter(tag = self).values_list('issue', flat = True)
        return Issue.objects.filter(pk__in = issue_ids).distinct()
    
    
    
class TaggedIssue(models.Model):
    issue = models.ForeignKey(Issue)
    tag = models.ForeignKey(Tag)
    user = models.ForeignKey(User)

    class Meta:
        unique_together = (('issue', 'tag', 'user'),)

