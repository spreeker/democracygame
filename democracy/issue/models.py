"""
Issue model , objects on which we vote
(whished) functionality
TODO
-Update possibilities on issues? history and undo?
-location (geo django) data?
-language field?
"""
from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin

from django.utils.translation import ugettext_lazy as _
from issue.managers import IssueManager
from issue.managers import LawManager 
from issue.managers import ActiveManager 
from issue.fields import AutoSlugField

import tagging

source_types = (
    (u"website", _(u"website")),
    (u"video", _(u"video")),
    (u"audio", _(u"audio")),
    (u"book", _(u"book")),
    (u"document", _(u"document")),
    (u"image", _(u"image")),
)


class Issue(models.Model):
    """
    Issue which we are supposed to vote on
    """
    user = models.ForeignKey(User)
    title = models.CharField(blank=True, max_length=200)
    slug = AutoSlugField(['title'], max_length=50, unique=True) 
    #slug = models.SlugField( max_length=80, null=True, unique=True)
    time_stamp = models.DateTimeField(default= datetime.now() )
    url = models.URLField(verify_exists=False)
    source_type = models.CharField(max_length=20, choices=source_types)
    body = models.TextField(max_length=2000)

    is_draft = models.BooleanField( default=True )

    # Denormalized data - for sort order
    offensiveness = models.IntegerField(default=0)
    score = models.IntegerField(default=0)
    hotness = models.IntegerField(default=0)
    votes = models.IntegerField(default=0)
    
    objects = IssueManager()
    active = ActiveManager()
    laws =  LawManager()

    def __unicode__(self):
        return self.title
       

tagging.register(Issue)


class IssueAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug' : ("title",)} 

    date_hierarchy = "time_stamp"
    list_display = ('title', 'time_stamp', 'user', 'is_draft' ) 
    list_filter = ('title', 'time_stamp', 'user', 'is_draft' )

    def votes(self , obj):
        return Vote.objects.get_for_object(obj).count()


admin.site.register(Issue, IssueAdmin)

