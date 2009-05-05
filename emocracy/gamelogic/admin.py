# by Thijs Coenen  for the Emocracy project
from django.contrib import admin

from models import Mandate, LawProposal, Motion, IssueBody


admin.site.register(Mandate)
admin.site.register(LawProposal)
admin.site.register(Motion)
admin.site.register(IssueBody)