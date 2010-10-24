from datetime import datetime

from django.db import models, IntegrityError
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext as _


from voting.models import Vote

class IssueManager(models.Manager):
    """ deal with all issues 
    """
    pass


class ActiveManager(models.Manager):
    """ deal with all active issues
        which are the ones with is_draf = False for now
    """

    def get_query_set(self):
        return super(ActiveManager, self).get_query_set().filter(is_draft=False)
        

class ParliamentManager(models.Manager):
    """ deal with issues which should be on the parliament agenda 
   
    curent plan:
    -get all parliament members
    -get all votes with their id's on issues
    -exclude votes on laws!
    -sort those on count

    This issue list should be the agenda.
    
    """
    pass


class LawManager(models.Manager):
    """ deal with issues which are law """

    def get_query_set(self):
        law_issues = Vote.parliament.get_for_model(self.model)
        law_issues = law_issues.values('object_id')

        return super(LawManager, self).get_query_set().filter(id__in=law_issues)

