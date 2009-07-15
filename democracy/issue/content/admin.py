
from django.contrib import admin
from models import IssueBody 


class IssueBodyAdmin(admin.ModelAdmin):
    fields = ( 'body' , 'url' , 'source_type' )
 
admin.site.register(IssueBody, IssueBodyAdmin)
