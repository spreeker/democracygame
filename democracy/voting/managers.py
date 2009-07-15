from datetime import datetime

from django.db import models, IntegrityError
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext as _


class IssueManager(models.Manager):
    def get_for_object(self, obj):
        ctype = ContentType.objects.get_for_model(obj)
        return self.filter(content_type = ctype.pk,
            object_id = obj.pk)

    def create_for_object(self, obj, *args, **kwargs):
        title = kwargs.pop('title', '')
        owner = kwargs.pop('owner', None)
        new_issue = self.create(
            owner = owner,
            title = title,
            time_stamp = datetime.now(),
            payload = obj,
        )        
        return new_issue

    def with_counts(self, offset=0, limit=100):
        #TODO make this a qs?
        """ return issues with total votes on them 
            issue.vote # vote value
            issue.vote_count # count of vote value
        """

        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("""
            SELECT i.id, i.title, i.time_stamp , v.vote , COUNT(*)
            FROM voting_issue i, voting_vote v
            WHERE i.id = v.issue_id 
            GROUP BY 1, 2, 3, 4 
            ORDER BY 3 DESC
            OFFSET %d 
            LIMIT %d """ % (offset , limit) 
        )
        result_list = []

        for row in cursor.fetchall():
            i = self.model(id=row[0], title=row[1], time_stamp=row[2])
            i.vote = row[3]
            i.vote_count = row[4]
            result_list.append(i)
        return result_list

class VoteManager(models.Manager):
    def get_user_votes(self, user):
        return Vote.objects.filter(owner=user, is_archived=False).order_by("time_stamp").reverse()

    def vote(self, vote):
        """
        Archive old votes by switching the is_archived flag to True
        for all the previous votes on <issue> by <user>.
        And we check for and dismiss a repeated vote.
        We save old votes for research, probable interesting
        opinion changes.
        """
        votes = self.filter(owner=vote.owner, is_archived=False, issue=vote.issue)
        voted_already = False
        repeated_vote = False
        if votes:
            voted_already = True
            for v in votes:
                if vote.vote == v.vote: #check if you do the same vote again.
                    repeated_vote = True
                else:
                    v.is_archived = True
                    v.save()            

        if not repeated_vote:
            vote.save()

        return repeated_vote, voted_already
