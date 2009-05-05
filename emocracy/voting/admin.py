# by Thijs Coenen  for the Emocracy project
from django.contrib import admin

from models import Tag, TaggedIssue, Issue, IssueSet
admin.site.register(Tag)
admin.site.register(TaggedIssue)

admin.site.register(IssueSet)
admin.site.register(Issue)
