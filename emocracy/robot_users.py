# setup the correct enivironment variables :
from django.core.management import setup_environ
import settings
setup_environ(settings)
# now continue as per usual:
import datetime, random, codecs, sys
from django.contrib.auth.models import User
from profiles.models import UserProfile

user_names = """
ana alexander bert barbara carmen chantal dirk diederik ditke dedeke ernie frederik ferdinand
fred fanny george gijs hans helena henriette herbert irene ien jasper jorn judas klaas karel karla kees lara lianne
mees mohammed nick nicolette piet peter petra rianne roderik sietske suzanne
"""


def create_users():
    l = user_names.split()
    for x in l:
        try:
            u = User.objects.create_user(x, 'tcoenen@science.uva.nl', 'demo')
            u.save()
            np = UserProfile(user = u, score = 0, role = 'citizen')
            np.save()
        except:
            print "failed to create :", x

if __name__ == "__main__":
    create_users()
