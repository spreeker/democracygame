from django.db import models
from django.contrib.sites.models import Site
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

class Chunk(models.Model):
    """
    A Chunk is a piece of content associated
    with a unique key that can be inserted into
    any template with the use of a special template
    tag
    """
    key = models.CharField(help_text="A unique name for this chunk of content", blank=False, max_length=255)
    content = models.TextField(blank=True)
    lang_code = models.CharField(verbose_name=_(u"language"), help_text="Language code, if this chunk is translated. Same format as LANGUAGE_CODE setting, e.g. sv-se, or de-de, etc.", blank=True, max_length=5, default=settings.LANGUAGE_CODE)
    site = models.ForeignKey(Site, default=settings.SITE_ID, blank=True, null=True, verbose_name=_('site'))

    class Meta:
        unique_together = (('key', 'lang_code', 'site'),)

    def __unicode__(self):
        return u"%s" % (self.key,)
