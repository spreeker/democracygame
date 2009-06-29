"""This is the core of the Emocracy voting system. The Issue model in this 
module can be generically linked to anything that users whould be able to vote
on.

This module implements:
-voting database interactions
-tagging database interactions

Note that game rules should not be added to this module.
"""

from datetime import datetime

from django.db import models, IntegrityError
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext as _

from voting.managers import IssueManager

# ADD NEW POSSIBILITIES WITH NEW INTEGERS, THEY NEED TO BE UNIQUE
# LEAVE OLD ENTRIES SO AS NOT TO MESS THE DATABASE UP!

normal_votes = (
    (-1 , _(u"Against")),
    (1 , _(u"For")),
)

blank_votes = [
    # content related problems with issues:
    (10, _(u'Unconvincing')),
    (11, _(u'Not political')),
    (12, _(u'Can\'t completely agree')),
    # form related problems with issues":
    (13, _(u"Needs more work")),
    (14, _(u"Badly worded")),
    (15,  _(u"Duplicate")),
    (16, _(u'Unrelated source')),
    # personal considerations:
    (17, _(u'I need to know more')),
    (18, _(u'Ask me later')),
    (19, _(u'Too personal')),
]

possible_votes = list(normal_votes)
possible_votes.extend(blank_votes)
votes_to_description = dict(possible_votes)


class Issue(models.Model):
    """
    voting issue. 
    
    # create an issue. 
    >>> from issues_content.models import IssueBody
    >>> tuser = User.objects.create_user('john', 'john@john.com', 'pass')
    >>> tissue = IssueBody.objects.create( owner = tuser, title = 'tissue',body = 'body',url = 'tissue.org',source_type = 'website', time_stamp = datetime.now())
    >>> tissue = Issue.objects.create_for_object(tissue, title=tissue.title, owner=tissue.owner)
    >>> tissue.vote(tuser, -1, False)
    <Vote: -1 on "tissue" by john>

    """
    owner = models.ForeignKey(User)
    title = models.CharField(blank = True, max_length = 200)
    time_stamp = models.DateTimeField()
    
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField() 
    payload = generic.GenericForeignKey('content_type', 'object_id')

    is_draft = models.BooleanField( default = True )

    # Denormalized data - for sort order
    offensiveness = models.IntegerField(default = 0)
    score = models.IntegerField(default = 0)
    votes = models.IntegerField(default = 0)
    hotness = models.IntegerField(default = 0)
    
    objects = IssueManager()
    
    class Meta:
        unique_together = (('content_type', 'object_id') , ("owner" ,"title" ) ) 

    def __unicode__(self):
        return self.title

    def vote(self, user, vote_int, keep_private):
        new_vote = Vote.objects.create(
            owner = user,
            issue = self,
            vote = vote_int,
            keep_private = keep_private,
            time_stamp = datetime.now()
        )
        self.votes += 1
        self.save()
        return new_vote

    def vote_count( self ):
        """return dict with vote : value as key : value pair
        """
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("""
           SELECT v.vote , COUNT(*)
           FROM voting_vote v
           WHERE %d = v.issue_id 
           GROUP BY 1
           ORDER BY 1 """ % ( self.id ) 
        )
        votes = {} 

        for row in cursor.fetchall():
           votes[row[0]] = row[1]

        return votes       

    def tag(self, user, tag_string):
        # this code should not be here!!!
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
    title = models.CharField( unique = True , max_length = 200)
    body = models.TextField(max_length = 2000)
    time_stamp = models.DateTimeField()
    issues = models.ManyToManyField(Issue) # add a trough keyword later ...
    users = models.ManyToManyField(User, related_name = 'pollusers')
    
    def __unicode__(self):
        return self.title
        

class VoteManager(models.Manager):
    def get_user_votes( self , user ):
        user_votes = Vote.objects.filter(owner = user, is_archived = False).order_by("time_stamp").reverse()
        # beter paginate this qs when you use it!
        return user_votes 

    
class Vote(models.Model):
    api_interface = models.CharField(max_length = 50, blank = True)
    owner = models.ForeignKey(User)
    issue = models.ForeignKey(Issue)
    vote = models.IntegerField(choices = possible_votes)
    time_stamp = models.DateTimeField(editable = False , default=datetime.now )
    is_archived = models.BooleanField(default = False)
    keep_private = models.BooleanField(default = False)
   
    objects = VoteManager()

    def __unicode__(self):
        return unicode(self.vote) + u" on \"" + self.issue.title + u"\" by " + self.owner.username

# Rationale: Django-tagging does not keep counts of the number of tags for an
# model. I need that number because a new tag should only show up after
# a certain number of users have used it (on any Issue, so Model wide counts
# will suffice). On the other hand the only things that can be tagged in
# Emocracy are Issues/stuff you can vote on - so there is no need to user the
# generic foreign key facilities in Django

# OPTION use default tagging. but wrap if with game specific tagging functions
# this should be in a separate taggin app!!

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

