# by Thijs Coenen  for the Emocracy project
from django.contrib import admin

from models import Tag
from models import TaggedIssue
from models import Issue
from models import IssueSet

class IssueAdmin(admin.ModelAdmin):
    date_hierarchy = "time_stamp"
    list_display = ('title', 'time_stamp', 'owner' , 'votes') 
    list_filter = ( 'title' , 'time_stamp', 'owner' , 'votes')

admin.site.register(Tag)
admin.site.register(TaggedIssue)
admin.site.register(IssueSet)
admin.site.register(Issue , IssueAdmin)
