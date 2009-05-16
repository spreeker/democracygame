
from django.contrib.auth.models import User
from piston.handler import BaseHandler, AnonymousBaseHandler
from piston.utils import rc

from emocracy.issues.models import IssueBody

class AnonymousUserListHandler(AnonymousBaseHandler):
    allowed_methods = ('GET',)
    fields = ('user_uri', 'username')
    exclude = ('absolute_uri',)
    model = User

    def read(self, request, *args, **kwargs):
        return self.model.objects.filter()

    @staticmethod
    def user_uri(user):
        return 'http://emo.buhrer.net/api/users/%s/' %user.id

class UserListHandler(BaseHandler):
    allowed_methods = ('GET',)
    fields = ('user_uri', 'username')
    anonymous = AnonymousUserListHandler
    model = User

    @staticmethod
    def read(self, request, *args, **kwargs):
        return self.model.objects.filter()

    @staticmethod
    def user_uri(user):
        return 'http://emo.buhrer.net/api/users/%s/' %user.id

class AnonymousUserHandler(AnonymousBaseHandler):
    allowed_methods = ('GET',)
    fields = ('username', 'score', 'user_uri')
    model = User

    def read(self, request, id, *args, **kwargs):
        return self.model.objects.filter(id=id)

    @staticmethod
    def score(user):
        return user.get_profile().score

    @staticmethod
    def user_uri(user):
        return 'http://emo.buhrer.net/api/users/%s/' %user.id

class UserHandler(BaseHandler):
    allowed_methods = ('GET',)
    fields = ('username', 'score', 'user_uri')
    anonymous = AnonymousUserHandler
    model = User

    def read(self, request, id, *args, **kwargs):
        return self.model.objects.filter(id=id)

    def score(self, user):
        return user.get_profile().score

    def resource_uri(self, user):
        return 'http://emo.buhrer.net/api/users/%s/' %user.id

class AnonymousIssueListHandler(AnonymousBaseHandler):
    allowed_methods = ('GET',)
    fields = ('issue_uri', 'title', ('owner', ('username', 'user_uri',)),                'time_stamp')
    model = IssueBody

    def read(self, request, *args, **kwargs):
        return self.model.objects.filter()

    @staticmethod
    def user_uri(user):
        return 'http://emo.buhrer.net/api/users/%s/' %user.id

    @staticmethod
    def issue_uri(issue):
        return 'http://emo.buhrer.net/api/issues/%s/' %issue.id

class IssueListHandler(BaseHandler):
    allowed_methods = ('GET',)
    anonymous = AnonymousIssueListHandler
    fields = ('issue_uri', 'title', ('owner', ('username', 'user_uri',)),               'time_stamp')
    model = IssueBody
    
    def read(self, request, *args, **kwargs):
        return self.model.objects.filter()
    
    @staticmethod
    def user_uri(user):
        return 'http://emo.burher.net/api/users/%s/' %user.id

    @staticmethod
    def issue_uri(issue):
        return 'http://emo.buhrer.net/api/issues/%s/' %issue.id

class AnonymousIssueHandler(AnonymousBaseHandler):
    allowed_methods = ('GET',)
    fields = ('issue_uri', 'title', 'body', ('owner', ('username', 'user_uri',)), 'time_stamp', 'source_type', 'url')
    model = IssueBody

    def read(self, request, id, *args, **kwargs):
        return self.model.objects.filter(id=id)

    @staticmethod
    def user_uri(user):
        return 'http://emo.buhrer.net/api/users/%s/' %user.id

    @staticmethod
    def issue_uri(issue):
        return 'http://emo.buhrer.net/api/issues/%s/' %issue.id

class IssueHandler(BaseHandler):
    allowed_methods = ('GET',)
    anonymous = AnonymousIssueHandler
    fields = ('issue_uri', 'title', 'body', ('owner', ('username', 'user_uri',)), 'time_stamp', 'souce_type', 'url')
    model = IssueBody
        
    def create(self, request):
        attrs = self.flatten_dict(request.POST)

        if self.exists(**attrs):
            return rc.DUPLICATE_ENTRY
        else:
            issue = IssueBody(title=attrs['title'], 
                            content=attrs['body'],
                            url=attrs['url'],
                            source_type=attrs['source_type'],
                            owner=request.user)
            issue.save()
            
            return issue
    
    def read(self, request, id):
        if id==None:
            return self.model.objects.filter()
        else:
            return self.model.objects.filter(id=id)
    
    @staticmethod
    def user_uri(user):
        return 'http://emo.buhrer.net/api/users/%s/' %user.id

    @staticmethod
    def issue_uri(issue):
        return 'http://emo.buhrer.net/api/issues/%s/' %issue.id
