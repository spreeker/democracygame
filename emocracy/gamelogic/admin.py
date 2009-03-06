# by Thijs Coenen  for the Emocracy project
from django.contrib import admin

from models import Mandate, IssueTag, TaggedIssue
from models import Votable, LawProposal, Motion, IssueBody, VotableSet


admin.site.register(Mandate)
admin.site.register(IssueTag)
admin.site.register(TaggedIssue)

admin.site.register(VotableSet)
admin.site.register(Votable)
admin.site.register(LawProposal)
admin.site.register(Motion)
admin.site.register(IssueBody)