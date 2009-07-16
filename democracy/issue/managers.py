from datetime import datetime

from django.db import models, IntegrityError
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext as _

class IssueManager(models.Manager):

    def hot(self):
        pass

    def new(self):
        pass

    def user_issues(self, user):
        pass


