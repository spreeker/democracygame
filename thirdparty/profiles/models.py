from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique = True)
    signature = models.TextField(blank = True)
    url = models.URLField(verify_exists = False, blank = True)
    id_is_verified = models.BooleanField(default = False)
    timezone = models.CharField(max_length = 100, default="Europe/London")
    access_token = models.CharField(max_length=400, blank=True)
    access_secret = models.CharField(max_length=400, blank=True)
    
