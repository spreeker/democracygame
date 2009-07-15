from django.contrib import admin

from models import Issue
from models import Vote

class IssueAdmin(admin.ModelAdmin):
    date_hierarchy = "time_stamp"
    list_display = ('title', 'time_stamp', 'owner', 'votes' ) 
    list_filter = ('title', 'time_stamp', 'owner', 'votes' )

    def votes(self , obj):
        return Vote.objects.filter( issue=obj.id).count()

class VoteAdmin(admin.ModelAdmin):
    date_hierarchy = "time_stamp"
    list_display = ('vote', 'issue_title', 'owner', 'time_stamp')
   
    list_filter = ('owner', 'time_stamp', 'issue')

    def issue_title(self , obj):
        return ("%s" % obj.issue.title) 
    
admin.site.register(Issue , IssueAdmin)
admin.site.register(Vote, VoteAdmin)
