
from django.db import models
from django.contrib.auth.models import User

from emocracy.voting.models import Issue

tag_count_threshold = 1
MAX_MULTIPLIES = 4

roles = ["anonymous citizen", 
        "citizen", 
        "active citizen", 
        "opinion leader", 
        "candidate", 
        "parliament member", 
        "minister", 
        'prime minister']

class MultiplyIssue(models.Model):
    user = models.ForeignKey(User, unique = True)
    time_stamp = models.DateTimeField(auto_now_add = True)
    issue = models.ForeignKey( Issue )
    downgrade = models.BooleanField( default = False )

    def __unicode__(self):
        return _(u'%(user)s  multiplies for %(issue)s' % {
            'user' : self.user.username,
            'issue' : self.issue.title, 
            })

    def save(self, force_insert=False, force_update=False):
        """ Multiply an issue
            only if your limit is not reached.

            Maybe this can be extended for users at different levels to have different multiplies
        """
        count_m = MultiplyIssue.objects.filter( user = user ).count()
        if count_m < MAX_MULTIPLIERS:
            if not self.issue.owner == user:
                super(Entry, self).save(force_insert, force_update)
        #TODO write a message to the user? 
