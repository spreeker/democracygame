from django.db import models, IntegrityError
from django.db import connection
from django.db.models import Avg, Count, Sum

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
normal_votes = votes.copy()
normal_votes.update(blank_votes)

multiply_votes = {
    20 : _("Multiply"),
}

possible_votes = normal_votes.copy() 
possible_votes.update(multiply_votes)


class VoteManager(models.Manager):

    def get_for_object(self, obj):
        """
        Get qs for votes on object
        """
        ctype = ContentType.objects.get_for_model(obj)
        return self.filter(content_type = ctype.pk,
            object_id = obj.pk)

    def get_for_user(self, user , obj):
        """
        Get the vote made on an give object by user return None if it not exists
        """
        object_id = obj._get_pk_val()
        ctype = ContentType.objects.get_for_model(obj)
        try:
            return self.get(content_type=ctype, object_id=object_id, is_archived=False, user=user )
        except Vote.DoesNotExist:
            return None 

    def get_for_user_in_bulk(self, user, objects):
        """
        Get dictinary mapping object to vote for user on given objects.
        """
        object_ids = [o._get_pk_val() for o in objects]
        if not object_ids:
            return {}
        if not user.is_authenticated():
            return {} 

        qs = self.filter( user=user )
        qs = qs.filter( is_archived=False )
        ctype = ContentType.objects.get_for_model(objects[0])
        qs = qs.filter(content_type=ctype, object_id__in=object_ids)
        votes = list(qs)
        vote_dict = dict([( vote.object_id, vote ) for vote in votes ])
        return vote_dict

    def get_user_votes(self, user, obj=None):
        """
        Get qs for active votes by user
        """
        return self.filter(user=user, is_archived=False).order_by("-time_stamp")
    
    def get_object_votes(self, obj, all=False):
        """
        Get a dictionary mapping vote to votecount
        """
        object_id = obj._get_pk_val()
        ctype = ContentType.objects.get_for_model(obj)
        qs = self.filter(content_type=ctype, object_id=object_id)
    
        if not all:
            qs = qs.filter(is_archived=False) # only pick active votes

        qs = qs.values('vote')
        qs = qs.annotate(vcount=Count("vote")).order_by()

        vote_dict = {}
        
        for count in qs:
            if count['vote'] >= 10 : # sum up all blank votes
                vote_dict[0] = vote_dict.get(0,0) + count['vcount']
            vote_dict[count['vote']] = count['vcount']

        return vote_dict

    def get_for_objects_in_bulk(self, objects, all=False):
        """
        Get a dictinary mapping objects ids to dictinary
        which maps direction to votecount
        """
        object_ids = [o._get_pk_val() for o in objects]
        if not object_ids:
            return {}
        ctype = ContentType.objects.get_for_model(objects[0])
        qs = self.filter(content_type=ctype, object_id__in=object_ids)

        if not all: # only pick active votes
            qs = qs.filter(is_archived=False) 

        qs = qs.values('object_id', 'vote',)
        qs = qs.annotate(vcount=Count("vote")).order_by()
       
        vote_dict = {}
        for votecount  in qs:
            object_id = votecount['object_id']
            votes = vote_dict.setdefault(object_id , {})
            if votecount['vote'] >= 10:  # sum up all blank votes
                votes[0] = votes.get(0,0) + votecount['vcount']
            votes[votecount['vote']] =  votecount['vcount']

        return vote_dict

    def get_popular(self, Model, object_ids=None):
        """ return qs ordered by popularity """
        ctype = ContentType.objects.get_for_model(Model)
        qs = self.filter(content_type=ctype,)
        qs = qs.filter(is_archived=False) 

        if object_ids: # to get the most popular from a list
            qs = qs.filter(object_id__in=object_ids)

        qs = qs.values('object_id',)
        qs = qs.annotate(totalvotes=Count("vote")).order_by()
        qs = qs.order_by('-totalvotes')
        #qs = qs.values_list('object_id' , 'totalvotes')
       
        return qs

    def get_count(self, Model, object_ids=None, direction=1):
        """
        Find list ordered by count of votes for a direction.
        """
        ctype = ContentType.objects.get_for_model(Model)
        qs = self.filter(content_type=ctype,)
        qs = qs.filter(is_archived=False) 

        if object_ids: # to get the most popular from a list
            qs = qs.filter(object_id__in=object_ids)
        
        qs = qs.values('object_id',)
        qs = qs.filter(vote=direction)
        qs = qs.annotate(totalvotes=Count("vote")).order_by()
        qs = qs.order_by('-totalvotes')
        
        return qs

    def get_top(self, Model, object_ids=None, reverse=False):
        """
        Find the votes which are possitive recieved.
        """
        ctype = ContentType.objects.get_for_model(Model)
        qs = self.filter(content_type=ctype,)
        qs = qs.filter(is_archived=False) 

        if object_ids: # to get the most popular from a list
            qs = qs.filter(object_id__in=object_ids)
        
        qs = qs.values('object_id',)
        qs = qs.filter(vote__in=[-1,1])
        qs = qs.annotate(totalvotes=Count("vote"))
        qs = qs.filter(totalvotes__gt=2) 
        qs = qs.annotate(avg=Avg("vote")).order_by()
        if reverse:
            qs = qs.order_by('avg')
        else:
            qs = qs.order_by('-avg')
        
        return qs

    def get_bottom(self, Model, object_ids=None):
        """
        Find the votes which are worst recieved
        """
        qs = self.get_top(Model, object_ids, reverse=True)

        return qs

    def get_controversial(self, Model, object_ids=None):
        """ 
        return qs ordered by controversy , 
        meaning it divides the ppl in 50/50.
        since for is 1 and against is -1, a score close to 0
        indicates controversy.
        """
        ctype = ContentType.objects.get_for_model(Model)
        qs = self.filter(content_type=ctype,)
        qs = qs.filter(is_archived=False) 
        qs = qs.filter(vote__in=[-1,1])

        if object_ids: # to get the most popular from a list
            qs = qs.filter(object_id__in=object_ids)

        qs = qs.values('object_id',)
        qs = qs.annotate(avg=Avg("vote")).order_by()
        qs = qs.order_by('avg')
        qs = qs.filter(avg__gt= -0.3 )
        qs = qs.filter(avg__lt= 0.3 )
        #qs = qs.values_list('object_id' , 'avg')

        return qs

    def get_for_direction(self, Model, directions=[1,-1]):
        """
        return objects with a specific direction for ...
        TODO
        """
        ctype = ContentType.objects.get_for_model(Model)
        qs = self.filter(content_type=ctype,)
        qs = qs.filter(is_archived=False) 
        qs = qs.filter(vote__in=directions)

        return qs

    def record_vote(self, user, obj, direction, keep_private=False, api_interface=None):
        """
        Archive old votes by switching the is_archived flag to True
        for all the previous votes on <obj> by <user>.
        And we check for and dismiss a repeated vote.
        We save old votes for research, probable interesting
        opinion changes.
        """
        if not direction in possible_votes.keys():
            raise ValueError('Invalid vote %s must be in %s' % (direction, possible_votes.keys()))

        ctype = ContentType.objects.get_for_model(obj)
        votes = self.filter(user=user, content_type=ctype, object_id=obj._get_pk_val(), is_archived=False)

        voted_already = False
        repeated_vote = False
        if votes:
            voted_already = True
            for v in votes:
                if direction == v.vote: #check if you do the same vote again.
                    repeated_vote = True
                else:
                    v.is_archived = True
                    v.save()            
        vote = None
        if not repeated_vote:
            vote = self.create( user=user, content_type=ctype,
                         object_id=obj._get_pk_val(), vote=direction,
                         api_interface=api_interface, is_archived=False, 
                         keep_private=keep_private
                        )
            vote.save()
        return repeated_vote, voted_already, vote
