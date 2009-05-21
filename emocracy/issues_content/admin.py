
from django.contrib import admin
from models import IssueBody 


class IssueBodyAdmin(admin.ModelAdmin)
    fields = ( 'body' , 'url' , 'source_type' )
    search_fields = ( 'owner' , 'title' )
    
admin.site.register(IssueBodyi, IssueBodyAdmin)
