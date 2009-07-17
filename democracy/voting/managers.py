from django.db import models, IntegrityError
from django.db import connection
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext as _

votes = {
    -1 : _(u"Against"),
    1  : _(u"For"),
}
blank_votes = {
    # content related problems with issues:
    10 : _(u'Unconvincing'),
    11 : _(u'Not political'),
    12 : _(u'Can\'t completely agree'),
    # form related problems with issues":
    13 : _(u"Needs more work"),
    14 : _(u"Badly worded"),
    15 : _(u"Duplicate"),
    16 : _(u'Unrelated source'),
    # personal considerations:
    17 : _(u'I need to know more'),
    18 : _(u'Ask me later'),
    19 : _(u'Too personal'),
}
possible_votes = votes
possible_votes.update(blank_votes)


class VoteManager(models.Manager):

    def get_for_object(self, obj):
        ctype = ContentType.objects.get_for_model(obj)
        return self.filter(content_type = ctype.pk,
            object_id = obj.pk)

    def get_user_votes(self, user):
        return Vote.objects.filter(owner=user, is_archived=False).order_by("time_stamp").reverse()
    
    def get_object_votes(self, obj):
        """
        return dict with vote : value as key : value pair
        """
        ctype = ContentType.objects.get_for_model(obj)

        cursor = connection.cursor()
        cursor.execute("""
           SELECT v.vote , COUNT(*)
           FROM votes v
           WHERE %d = v.object_id AND %d = v.content_type_id
           GROUP BY 1
           ORDER BY 1 """ % ( obj.id, ctype.id ) 
        )
        votes = {} 

        for row in cursor.fetchall():
           votes[row[0]] = row[1]

        return votes       

    def record_vote(self, user, obj, vote_int , api_interface=None ):
        """
        Archive old votes by switching the is_archived flag to True
        for all the previous votes on <obj> by <user>.
        And we check for and dismiss a repeated vote.
        We save old votes for research, probable interesting
        opinion changes.
        """
        if not vote_int in possible_votes.keys():
            raise ValueError('Invalid vote %s must be in %s' % (vote_int , possible_votes.keys()))

        ctype = ContentType.objects.get_for_model(obj)
        votes = self.filter(user=user, content_type=ctype, object_id=obj._get_pk_val())

        voted_already = False
        repeated_vote = False
        if votes:
            voted_already = True
            for v in votes:
                if vote_int == v.vote: #check if you do the same vote again.
                    repeated_vote = True
                else:
                    v.is_archived = True
                    v.save()            
        vote = None
        if not repeated_vote:
            vote = self.create( user=user , content_type=ctype,
                         object_id=obj._get_pk_val(), vote=vote_int,
                         api_interface=api_interface 
                        )
            vote.save()
        return repeated_vote, voted_already, vote
