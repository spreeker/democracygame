from django.db import models
from django.contrib.auth.models import User

from gamelogic.models import roles 

from django.db.models.signals import post_save

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
        return UserProfile.objects.filter(score__gte = self.score).count()


def create_userprofile(sender, **kwargs):
    """
    When a User model instance is saved this function is called to create
    a UserProfile instance if none exists already. (This function listens for
    post_save signals coming from the User model.)
    If you create a user anywhere , in the admin or
    official registration way , this code will make sure there is a userprofile. 
    """
    new_user = kwargs['instance']
    if kwargs["created"]:
        new_profile = UserProfile(user=new_user, score=0, role='citizen')
        new_profile.save()


post_save.connect(create_userprofile, sender=User, dispatch_uid="users-profilecreation-signal")


