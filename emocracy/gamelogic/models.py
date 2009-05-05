# By Thijs Coenen for the Emocracy project (october 2008).
import datetime

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext as _

from emocracy.voting.models import *

tag_count_threshold = 10


roles = [u"anonymous citizen", u"citizen", u"active citizen", u"opinion leader", u"candidate", u"parliament member", u"minister", u'prime minister']


class Mandate(models.Model):
    user = models.ForeignKey(User, unique = True)
    representative = models.ForeignKey(User, related_name = "representative")
    time_stamp = models.DateTimeField(auto_now_add = True)

    def __unicode__(self):
        return _(u'%(user)s voted for %(representative)s' % {
            'user' : self.user.username,
            'representative' : self.representative.username, # hits another table, might not be a good idea
            }) 

source_types = (
    (u"video", _(u"video")),
    (u"audio", _(u"audio")),
    (u"book", _(u"book")),
    (u"document", _(u"document")),
    (u"image", _(u"image")),
    (u"deeplink", _(u"deeplink")),
    (u"website", _(u"website")),
)

# ------------------------------------------------------------------------------

class IssueBody(models.Model):
    owner = models.ForeignKey(User)
    title = models.CharField(max_length = 200)
    body = models.TextField(max_length = 2000)
    source_type = models.CharField(max_length = 20, choices = source_types)
    url = models.URLField(verify_exists = False)
    time_stamp = models.DateTimeField()
    
    class Meta:
        verbose_name_plural = "issue bodies"

class LawProposal(models.Model):
    owner = models.ForeignKey(User)
    title = models.CharField(max_length = 200)
    body = models.TextField(max_length = 2000)
    on_issuebody = models.ForeignKey(IssueBody)
    time_stamp = models.DateTimeField()

class Motion(models.Model):
    owner = models.ForeignKey(User)
    title = models.CharField(max_length = 200)
    body = models.TextField(max_length = 2000)
    on_user = models.ForeignKey(User, related_name = 'on_user')
    time_stamp = models.DateTimeField()


