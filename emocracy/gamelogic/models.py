
from django.db import models
from django.contrib.auth.models import User

from emocracy.voting.models import Issue

tag_count_threshold = 1

roles = ["anonymous citizen", 
        "citizen", 
        "active citizen", 
        "opinion leader", 
        "candidate", 
        "parliament member", 
        "minister", 
        'prime minister']

class OpinionLeaderMultiply(models.Model):
    user = models.ForeignKey(User, unique = True)
    time_stamp = models.DateTimeField(auto_now_add = True)
    issue = models.ForeignKey( Issue )

    def __unicode__(self):
        return _(u'%(user)s  multiplies for %(issue)s' % {
            'user' : self.user.username,
            'issue' : self.issue.title, 
            })





