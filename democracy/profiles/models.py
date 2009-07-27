from django.db import models
from django.contrib.auth.models import User

from gamelogic.models import roles 


class UserProfile(models.Model):

    user = models.ForeignKey(User, unique = True)
    score = models.IntegerField(default = 0 ) 
    # game activity
    total_for = models.IntegerField(default = 0)
    total_against = models.IntegerField(default = 0)
    total_blank = models.IntegerField(default = 0)
    role = models.CharField(max_length = 30, choices=roles.items() )
    # description
    title = models.CharField(max_length = 100, blank = True)
    description = models.TextField(blank = True)
    url = models.URLField(verify_exists = False, blank = True)
    #privacy
    votes_public = models.BooleanField(default = False)
    id_is_verified = models.BooleanField(default = False)
    show_identity = models.BooleanField(default = False)


    def ranking(self):
        return UserProfile.objects.filter( score__gte = self.score ).count()
