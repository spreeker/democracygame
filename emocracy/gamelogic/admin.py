# by Thijs Coenen  for the Emocracy project
from django.contrib import admin

from models import Mandate, Tag, TaggedIssue
from models import Issue, LawProposal, Motion, IssueBody, IssueSet


admin.site.register(Mandate)
admin.site.register(Tag)
admin.site.register(TaggedIssue)

admin.site.register(IssueSet)
admin.site.register(Issue)
admin.site.register(LawProposal)
admin.site.register(Motion)
admin.site.register(IssueBody)