from django.utils.translation import ugettext as _
from django.db import models
from django.contrib.auth.models import User

from democracy.voting.models import Issue

tag_count_threshold = 1
MAX_MULTIPLIERS = 4

roles = ["anonymous citizen", 
        "citizen", 
        "active citizen", 
        "opinion leader", 
        "candidate", 
        "parliament member", 
        "minister", 
        'prime minister']

class MultiplyIssue(models.Model):
    owner = models.ForeignKey(User )
    time_stamp = models.DateTimeField(auto_now_add = True)
    issue = models.ForeignKey( Issue )
    downgrade = models.BooleanField( default = False )
    multiply_value = models.IntegerField( blank=True , null=True )

    def __unicode__(self):
        return _(u'%(owner)s  multiplies for %(issue)s' % {
            'owner' : self.owner.username,
            'issue' : self.issue.title, 
            })

    def save(self, force_insert=False, force_update=False):
        """ Multiply an issue
            only if your limit is not reached.

            Maybe this can be extended for users at different levels to have different multiplies
        """
        msg = "Failed to add Multiply"
        count_m = MultiplyIssue.objects.filter( owner = self.owner ).count()
        if count_m < MAX_MULTIPLIERS:
            if not self.issue.owner == self.owner :
                super(MultiplyIssue , self).save(force_insert, force_update)
                msg = "succes fully added multiply" 
                return self

        self.owner.message_set.create(message=msg)


