import datetime

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator
from django.core.paginator import InvalidPage
from django.core.paginator import EmptyPage
from django.contrib.contenttypes.models import ContentType

from piston.handler import BaseHandler, AnonymousBaseHandler
from piston.utils import rc
from piston.utils import validate

from democracy.api.forms import IssueForm
from democracy.api.forms import VoteForm
from democracy.issue.models import Issue
from democracy.voting.models import Vote
from democracy.profiles.models import UserProfile
from democracy.gamelogic.models import MultiplyIssue

import gamelogic.actions

from piston.models import Token

def paginate(request, qs):
    paginator = Paginator(qs, 3)  # TODO: add to settings.py
    try :
        pageno = int(request.GET.get('page', '1'))
    except ValueError:
        pageno = 1
    try :
        page = paginator.page(pageno)
    except (EmptyPage, InvalidPage):
        page = paginator.page(paginator.num_pages) #last page
    return page

class IssueVotesHandler(AnonymousBaseHandler):
    """
    Returns the vote count for an issue
    issue id should be provided
    Anonymous function it is about aggegrated data not user specific
    """ 
    allowed_methods = ('GET',)
    fields = ('vote', 'vote_count',)

    def read(self, request, id ,*args, **kwargs):
        try :
            issue = Issue.objects.get( id=id )
        except Issue.DoesNotExist :
            return rc.NOT_HERE
        
        votes = Vote.objects.get_object_votes( issue )
        return votes

    @classmethod
    def vote(cls, vote):
        return vote[0]

    @classmethod
    def vote_count(cls, vote):
        return vote[1]

    @staticmethod
    def resource_uri():
        return ('api_issue_votes' , ['id'])
    

class VoteHandler(BaseHandler):
    """
    returns the votes for an user. 
    makes it able to post to an user
    """
    allowed_methods = ('GET', 'POST' )
    fields = ('vote', 'time_stamp', 'issue_uri', 'keep_private', 'user_uri')
    model = Vote

    def read(self, request, *args, **kwargs):
        ctype = ContentType.objects.get_for_model(Issue)
        queryset = self.model.objects.filter( user = request.user,
                        content_type = ctype.pk ).order_by('time_stamp')
        page = paginate(request, queryset)
        return page.object_list

    @classmethod
    def issue_uri(cls, vote):
        return "%s" % reverse('api_issue' , args=[vote.object_id])

    @classmethod
    def user_uri(cls, vote):
        return "%s" % reverse('api_user' , args=[vote.user.id])

    ## TODO use the @validate decorator of piston
    @validate( VoteForm )
    def create(self, request ):
        ctype = ContentType.objects.get_for_model(Issue)
        attrs = self.flatten_dict(request.POST)
        object_id = attrs.pop('issue') 
        attrs.update({
                  'content_type' : ctype,
                  'object_id' : object_id,
                })

        if self.exists(**attrs):
            return rc.DUPLICATE_ENTRY
        if not attrs.has_key('keep_private'):
            attrs['keep_private'] = False
        
        #print type(request.throttle_extra)
    
        gamelogic.actions.vote( 
                request.user, 
                Issue.objects.get(id=attrs['object_id']),
                int(attrs['vote']),
                attrs['keep_private'],
                api_interface=request.throttle_extra,
        )
        return rc.CREATED 

class AnonymousUserHandler(AnonymousBaseHandler):
    allowed_methods = ('GET',)
    fields = ('username', 'score', 'ranking' , )
    model = User

    def read(self, request, id=None, *args, **kwargs):
        if id:
            try:
                return User.objects.filter( id=id )
            except User.DoesNotExist:
                return rc.NOT_FOUND
        else :
            queryset = User.objects.filter().order_by( 'username' )
            page = paginate(request, queryset)
            return page.object_list

    @classmethod
    def score(cls, user):
        return  get_profile_field(user, 'score', 0 )

    @classmethod
    def ranking(cls , user):
        score = cls.score(user) 
        return UserProfile.objects.filter( score__gte = score ).count()

    #TODO GRAVATAR url !! 

    @staticmethod
    def resource_uri():
        return ('api_user' , ['id'])


class UserHandler(BaseHandler):
    allowed_methods = ('GET',)
    fields = ('username', 'firstname' , 'lastname' , 'email' , 'score', 'ranking' , 'role' )
    anonymous = AnonymousUserHandler
    model = User

    def read(self, request, *args, **kwargs):
        return request.user

    @classmethod
    def score(cls, user):
        return get_profile_field(user, 'score' , 0)

    @classmethod
    def role( cls , user):
        return get_profile_field(user, 'role', 'citizen' )

    @classmethod
    def ranking( cls , user):
        score = cls.score(user)
        return UserProfile.objects.filter( score__gte = score ).count()

    @staticmethod
    def resource_uri():
        return ('api_user' , ['id'])


class AnonymousIssueHandler(AnonymousBaseHandler):
    allowed_methods = ('GET',)
    
    fields = ('title', 'body', ('user', ('username', ) ), 'time_stamp', 'source_type', 'url')
    model = Issue

    def read(self, request, id=None , *args, **kwargs):
        if id:
            return self.model.objects.filter( issue_id=id )
        else :
            queryset = self.model.objects.order_by( '-time_stamp' )
            page = paginate(request, queryset)
            return page.object_list

        queryset = self.model.objects.filter()
        page = paginate(request, queryset)
        return page.object_list

    @staticmethod
    def resource_uri():
        return ('api_issue' , ['id'])


class IssueHandler(BaseHandler):
    allowed_methods = ('POST',)
    anonymous = AnonymousIssueHandler
    fields = ('title', 'body', ('user', ('username')), 'time_stamp', 'souce_type', 'url')
    model = Issue

    @validate(IssueForm)
    def create(self, request):
        attrs = self.flatten_dict(request.POST)

        if self.exists(**attrs):
            return rc.DUPLICATE_ENTRY
        else :
            issue = gamelogic.actions.propose(
                request.user,
                attrs['title'],
                attrs['body'],
                attrs['vote_int'],
                attrs['url'],
                attrs['source_type'],
                attrs['is_draft'],
            )
            if issue : return rc.CREATED 
            else : rc.BAD_REQUEST

    @staticmethod
    def resource_uri():
        return ('api_issue' , ['id'])


class AnonymousMultiplyHandler( AnonymousBaseHandler ):
    allowed_methods = ('GET',)
    model = MultiplyIssue 

    fields = ( ('user', ('resource_uri') ), 'time_stamp' , ( 'issue' , ( 'resource_uri' ) ) )

    def read(self, request, id=None , *args, **kwargs):
        """ Read the active multiplies for specific issue
            or all multiplies in decending paginated order
        """
        if id:
            return self.model.objects.filter( issue=id )
        else :
            queryset = self.model.objects.all().order_by( '-time_stamp' )
            page = paginate(request, queryset)
            return page.object_list

        queryset = self.model.objects.filter()
        page = paginate(request, queryset)
        return page.object_list
    
    
    @staticmethod
    def resource_uri():
        return ('api_multiply' , ['id'])


class MultiplyHandler( BaseHandler ):
    """ If a user has enough game points the user can multiply the value
        of an issue.
    """
    allowed_methods = ('POST' , 'GET' )
    anonymous = AnonymousMultiplyHandler
    model = MultiplyIssue
    fields = ( ('user', ('resource_uri') ), 'time_stamp' , ( 'issue' , ( 'resource_uri' ) ) )

    #def read , default behaviour is what we want.    
    # which is readling all you own multiplies
    #TODO validate
    def create( self , request ):
        """ expects an issue id and optional a downgrade boolean
            in the POST data
        """
        attrs = self.flatten_dict(request.POST)

        issue = gamelogic.actions.multiply(
            request.user,
            Issue.objects.get( id = attrs['issue'] ) ,
            attrs.get('downgrade', False) ,
        )
        if issue : return rc.CREATED 
        else : return rc.BAD_REQUEST

    @staticmethod
    def resource_uri():
        return ('api_multiply' , ['id'])


# helper method.
def get_profile(user):
    try :
        return user.get_profile()
    except UserProfile.DoesNotExist:
        pass

def get_profile_field(user, property, default):
    profile = get_profile(user)
    if not profile: return default
    if hasattr(profile, property):
            return getattr(profile, property)
    return default
