"""
This is the core of the democracy voting system. The Issue model in this 
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
from voting.managers import VoteManager 

# ADD NEW POSSIBILITIES WITH NEW INTEGERS, THEY NEED TO BE UNIQUE
# LEAVE OLD ENTRIES SO AS NOT TO MESS THE DATABASE UP!

normal_votes = (
    (-1, _(u"Against")),
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
    (15, _(u"Duplicate")),
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
    >>> from issue_content.models import IssueBody
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
    hotness = models.IntegerField(default = 0)
    votes = models.IntegerField(default = 0)
    objects = IssueManager()
    
    class Meta:
        unique_together = (('content_type', 'object_id') , ("owner" ,"title" ) ) 

    def __unicode__(self):
        return self.title
   
    def vote_count(self):
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

            

class Vote(models.Model):
    api_interface = models.CharField(max_length=50, blank=True, null=True )
    owner = models.ForeignKey(User)
    issue = models.ForeignKey(Issue)
    vote = models.IntegerField(choices = possible_votes)
    time_stamp = models.DateTimeField(editable = False , default=datetime.now )
    is_archived = models.BooleanField(default = False)
    keep_private = models.BooleanField(default = False)
   
    objects = VoteManager()

    def __unicode__(self):
        return unicode(self.vote) + u" on \"" + self.issue.title + u"\" by " + self.owner.username

    class Meta:
        db_table = 'voting_vote'
