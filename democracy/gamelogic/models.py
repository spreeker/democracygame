from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.contrib.auth.models import User

from issue.models import Issue

MAX_MULTIPLIERS = 4

roles = {'anonymous citizen' : _(u'anonymous Citizen'), 
        'citizen' : _(u'citizen'),
        'active citizen' : _(u'active Citizen'),
        'opinion leader' : _(u'opinion Leader'),
        'candidate' : _(u'candidate'), 
        'parliament member' : _(u'parliament member'),
        'party program' : _(u'party program'),
        'minister' : _(u'minister'),
        'prime minister' : _(u'prime minister'),
}
human_roles = roles.copy()
human_roles.pop('party program')


class MultiplyIssue(models.Model):
    user = models.ForeignKey(User )
    time_stamp = models.DateTimeField(auto_now_add = True)
    issue = models.ForeignKey( Issue )
    downgrade = models.BooleanField( default = False )
    multiply_value = models.IntegerField( blank=True , null=True )

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
        msg = _("You have no multiplies left")
        count_m = MultiplyIssue.objects.filter( user = self.user ).count()
        if count_m < MAX_MULTIPLIERS:
            msg = _("You cannot not multiplie on your own issues")
            if not self.issue.user == self.user:
                super(MultiplyIssue , self).save(force_insert, force_update)
                msg = _("succesfully added multiply")
                return self

        self.user.message_set.create(message=msg)
