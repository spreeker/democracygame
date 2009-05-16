"""
Emocracy issue data. These models define issues on which people can vote.

(whished) functionality
-We define possible source types here and content.
-Update possibilities on issues? history and undo?
-location (geo django) data?
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

source_types = (
    (u"video", _(u"video")),
    (u"audio", _(u"audio")),
    (u"book", _(u"book")),
    (u"document", _(u"document")),
    (u"image", _(u"image")),
    (u"website", _(u"website")),
)

# TODO
# HOW TO DEAL with updated content?
# Add location to the Issue Body?

class IssueBody(models.Model):
    owner = models.ForeignKey(User)
    title = models.CharField(max_length = 200)
    body = models.TextField(max_length = 2000)
    source_type = models.CharField(max_length = 20, choices = source_types)
    url = models.URLField(verify_exists = False)
    time_stamp = models.DateTimeField()

    class Meta:
        verbose_name_plural = "issue bodies"

    def get_api_url():
        return "/api/issues/"+self.id+"/"
