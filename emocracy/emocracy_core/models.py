# By Thijs Coenen for the Emocracy project (october 2008).
import datetime

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext as _

tag_count_threshold = 10

source_types = (
    (u"video", _(u"video")),
    (u"audio", _(u"audio")),
    (u"boek", _(u"boek")),
    (u"document", _(u"document")),
    (u"image", _(u"image")),
    (u"deeplink", _(u"deeplink")),
    (u"website", _(u"website")),
)

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

roles = [u"anonymous citizen", u"citizen", u"active citizen", u"opinion leader", u"candidate", u"parliament member", u"minister", u'prime minister']

# ------------------------------------------------------------------------------
# -- New Style Emocracy internals ----------------------------------------------

class VotableManager(models.Manager):
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
        new_votable = self.create(
            owner = owner,
            title = title,
            time_stamp = datetime.datetime.now(),
            payload = obj,
        )        
        return new_votable

class Votable(models.Model):
    owner = models.ForeignKey(User)
    title = models.CharField(blank = True, max_length = 200)
    time_stamp = models.DateTimeField()
    
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField() # or just a IntegerField -> TODO find out!
    payload = generic.GenericForeignKey('content_type', 'object_id')
    
    # Denormalized data - for sort order and to give the db a break ;)
    offensiveness = models.IntegerField(default = 0)
    score = models.IntegerField(default = 0)
    votes = models.IntegerField(default = 0)
    hotness = models.IntegerField(default = 0)
    
    # TODO add fields for anymous votes (see wether they also need Vote
    # objects in the database)
    
    objects = VotableManager()
    
    class Meta():
        unique_together = ('content_type', 'object_id') # UNIQUENESS CONSTRAINT SEEMS TO BE IGNORED? FIXME

    def vote(self, user, vote_int, keep_private, votableset = None):
        new_vote = Vote.objects.create(
            owner = user,
            votable = self,
            votableset = votableset,
            vote = vote_int,
            keep_private = keep_private,
            time_stamp = datetime.datetime.now()
        )
        self.votes += 1 # See how this interacts with Emocracy design TODO
        self.save()
        return new_vote
    
    def tag(self, user, tag_string):
        # Get the tag object and if it does not exist yet, create it.
        try:
            tag = IssueTag.objects.get(name = tag_string)
            tag.count += 1
        except IssueTag.DoesNotExist:
            tag = IssueTag.objects.create(
                name = tag_string,
                first_suggested_by = user,
                count = 1
            )
        # Make tag visible if it is used enough times.
        if tag.count > tag_count_threshold:
            tag.visible = True
        tag.save()
        # Find out wether the user has tagged this issue already with this tag.
        try:
            ti = TaggedIssue.objects.get(
                votable = self,
                tag = tag,
                user = user
            )
            first_time = False
        except TaggedIssue.DoesNotExist:
            ti = TaggedIssue.objects.create(
                votable = self,
                tag = tag,
                user = user
            )
            first_time = True
        
        return tag, first_time
            
            
class VotableSet(models.Model):
    owner = models.ForeignKey(User)
    title = models.CharField(max_length = 200)
    body = models.TextField(max_length = 2000)
    time_stamp = models.DateTimeField()
    votables = models.ManyToManyField(Votable) # add a trough keyword later ...
    users = models.ManyToManyField(User, related_name = 'pollusers')
    
    def __unicode__(self):
        return self.title

class Vote(models.Model):
    owner = models.ForeignKey(User)
    votable = models.ForeignKey(Votable)
    votableset = models.ForeignKey(VotableSet, null = True)
    vote = models.IntegerField(choices = possible_votes)
    time_stamp = models.DateTimeField(editable = False)
    is_archived = models.BooleanField(default = False)
    keep_private = models.BooleanField(default = False)
    
    def __unicode__(self):
        return unicode(self.vote) + u" on \"" + self.votable.title + u"\" by " + self.owner.username

class Mandate(models.Model):
    user = models.ForeignKey(User, unique = True)
    representative = models.ForeignKey(User, related_name = "representative")
    time_stamp = models.DateTimeField(auto_now_add = True)

    def __unicode__(self):
        return _(u'%(user)s voted for %(representative)s' % {
            'user' : self.user.username,
            'representative' : self.representative.username, # hits another table, might not be a good idea
            }) 

class IssueBody(models.Model):
    owner = models.ForeignKey(User)
    title = models.CharField(max_length = 200)
    body = models.TextField(max_length = 2000)
    source_type = models.CharField(max_length = 20, choices = source_types)
    url = models.URLField(verify_exists = False)
    time_stamp = models.DateTimeField()

class LawProposal(models.Model):
    owner = models.ForeignKey(User)
    title = models.CharField(max_length = 200)
    body = models.TextField(max_length = 2000)
    on_issuebody = models.ForeignKey(IssueBody)
    time_stamp = models.DateTimeField()

class Motion(models.Model):
    owner = models.ForeignKey(User)
    title = models.CharField(max_length = 200)
    body = models.TextField(max_length = 2000)
    on_user = models.ForeignKey(User, related_name = 'on_user')
    time_stamp = models.DateTimeField()

# ------------------------------------------------------------------------------
# -- Bare bones Tagging implementation -----------------------------------------

# Rationale: Django-tagging does not keep counts of the number of tags for an
# model. I need that number because a new tag should only show up after
# a certain number of users have used it (on any Votable, so Model wide counts
# will suffice). On the other hand the only things that can be tagged in
# Emocracy are Issues/stuff you can vote on - so there is no need to user the
# generic foreign key facilities in Django

# Possible way to speed up get_for_votable: have a IssueTagField on an Issue
# (that would get rid of the TaggedIssue query).

class IssueTagManager(models.Manager):
    def get_for_votable(self, votable, max_num = 10):        
        tag_ids = TaggedIssue.objects.filter(votable = votable).values_list('tag', flat = True)
        return self.filter(pk__in = tag_ids).filter(visible = True).distinct().order_by('count').reverse()[:max_num]
    def get_popular(self, max_num = 10):
        return self.all().order_by('count').reverse()[:max_num]
        

class IssueTag(models.Model):
    """This is a tag, a """
    name = models.CharField(max_length = 50, unique = True)
    first_suggested_by = models.ForeignKey(User, null = True)
    points_awarded = models.BooleanField(default = False)
    visible = models.BooleanField(default = False)
    count = models.IntegerField(default = 0) # denormalized ... 
    objects = IssueTagManager()
    
    def __unicode__(self):
        return self.name
    
    def get_votables(self):
        votable_ids = TaggedIssue.objects.filter(tag = self).values_list('votable', flat = True)
        return Votable.objects.filter(pk__in = votable_ids).distinct()
        
    
class TaggedIssue(models.Model):
    votable = models.ForeignKey(Votable)
    tag = models.ForeignKey(IssueTag)
    user = models.ForeignKey(User)