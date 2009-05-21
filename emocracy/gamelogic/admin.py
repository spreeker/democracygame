# by Thijs Coenen  for the Emocracy project
from django.contrib import admin

from models import Mandate
from models import LawProposal
from models import Motion


admin.site.register(Mandate)
admin.site.register(LawProposal)
admin.site.register(Motion)
