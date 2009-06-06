

>>> from emocracy.gamelogic import levels
>>> from emocracy.profiles.models import UserProfiles
>>> from django.contrib.auth.models import User
>>> u = User.objects.create_user('testuser', 'test@example.com', 'testpw')
>>> np = UserProfile(user = u, score = 0, role = 'citizen')
>>> np.role()
>>> 'citizen'

>>> 

