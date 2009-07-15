import datetime

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator
from django.core.paginator import InvalidPage
from django.core.paginator import EmptyPage

from django.db.models import Q
from piston.handler import BaseHandler, AnonymousBaseHandler
from piston.utils import rc
from piston.utils import validate

from democracy.api.forms import IssueForm
from democracy.api.forms import VoteForm
from democracy.issue.content.models import IssueBody
from democracy.voting.models import Issue
from democracy.voting.models import Vote
from democracy.profiles.models import UserProfile
from democracy.gamelogic.models import MultiplyIssue

import gamelogic.actions


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
    Anonymous function it is global data not user specific
    """ 
    allowed_methods = ('GET',)
    fields = ('vote', 'vote_count',)

    def read(self, request, id ,*args, **kwargs):
        try :
            issue = Issue.objects.get( id=id )
        except Issue.DoesNotExist :
            return rc.NOT_HERE
        
        votes = issue.vote_count()
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
        queryset = self.model.objects.filter( owner = request.user ).order_by('time_stamp')
        page = paginate(request, queryset)
        return page.object_list

    @classmethod
    def issue_uri(cls, vote):
        return "%s" % reverse('api_issue' , args=[vote.issue.id])

    @classmethod
    def user_uri(cls, vote):
        return "%s" % reverse('api_user' , args=[vote.owner.id])

    ## TODO use the @validate decorator of piston
    @validate( VoteForm )
    def create(self, request , issue=None , vote=None):
        attrs = { 'issue' : issue , 'vote' : vote }
        attrs.update(self.flatten_dict(request.POST))

        if self.exists(**attrs):
            return rc.DUPLICATE_ENTRY
        if not attrs.has_key('keep_private'):
            attrs['keep_private'] = False

        vote = gamelogic.actions.vote( 
                request.user , 
                Issue.objects.get(id=attrs['issue']),
                attrs['vote'],
                attrs['keep_private'],
                api_interface = "API" , # TODO add aplication interface!!
        )
        return rc.CREATED 

    
class AnonymousUserHandler(AnonymousBaseHandler):
    allowed_methods = ('GET',)
    fields = ('username', 'score', 'ranking' , )
    model = User

    def read(self, request, id=None, *args, **kwargs):
        if id:
            return User.objects.filter( id=id )
        else :
            queryset = User.objects.filter()
            page = paginate(request, queryset)
            return page.object_list

    @classmethod
    def score(cls, user):
        return user.get_profile().score

    @classmethod
    def ranking(cls , user):
        p = user.get_profile()
        return UserProfile.objects.filter( score__gte = p.score ).count()

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
        return user.get_profile().score

    @classmethod
    def role( cls , user):
        return user.get_profile().role

    @classmethod
    def ranking( cls , user):
        p = user.get_profile()
        return UserProfile.objects.filter( score__gte = p.score ).count()

    @staticmethod
    def resource_uri():
        return ('api_user' , ['id'])


class AnonymousIssueHandler(AnonymousBaseHandler):
    allowed_methods = ('GET',)
    
    fields = ('title', 'body', ('owner', ('username', ) ), 'time_stamp', 'source_type', 'url')
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

    @classmethod
    def body( cls , issue ):
        return issue.payload.body        

    @classmethod
    def source_type( cls , issue):
        return issue.payload.source_type    
 
    @classmethod
    def url( cls , issue ):
        return issue.payload.url

    @staticmethod
    def resource_uri():
        return ('api_issue' , ['id'])


class IssueHandler(BaseHandler):
    allowed_methods = ('POST',)
    anonymous = AnonymousIssueHandler
    fields = ('title', 'body', ('owner', ('username')), 'time_stamp', 'souce_type', 'url')
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
                attrs['owners_vote'],
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

    fields = ( ('owner', ('resource_uri') ), 'time_stamp' , ( 'issue' , ( 'resource_uri' ) ) )

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
    fields = ( ('owner', ('resource_uri') ), 'time_stamp' , ( 'issue' , ( 'resource_uri' ) ) )

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
