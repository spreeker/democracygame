"""
The democracy API.

we have some public resources which you can get annonymousy
but for the private data we require oauth authentication
we have built test to acces those resouces through oauth.

"""
import datetime

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator
from django.core.paginator import InvalidPage
from django.core.paginator import EmptyPage
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType

from django.views.decorators.cache import cache_page
from django.views.decorators.cache import never_cache 

from piston.handler import BaseHandler, AnonymousBaseHandler
from piston.utils import rc
from piston.utils import validate

from api.forms import IssueForm
from api.forms import VoteForm
from api.forms import MultiplyForm
from issue.models import Issue
from voting.models import Vote
from profiles.models import UserProfile
from gamelogic.models import MultiplyIssue

from tagging.models import Tag, TaggedItem
from tagging.utils import calculate_cloud

import gamelogic.actions

from piston.models import Token


def paginate(request, qs, **kwargs):
    paginator = Paginator(qs, 25)  # TODO add to settings.py
    try:
        #pageno = int(request.GET.get('page', '1'))
        pageno = int(kwargs.get('page', '1'))
        # if we want cacheing on paginated results, 
        # page must be in url not in a parameter
        # issues/page/3 and not issues/?page=3
    except ValueError:
        pageno = 1
    try:
        page = paginator.page(pageno)
    except (EmptyPage, InvalidPage):
        page = paginator.page(paginator.num_pages) #last page
    return page


class IssueVotesHandler(AnonymousBaseHandler):
    """Return votes for issue
    """
    allowed_methods = ('GET', )
    fields = ('vote', 'vote_count', )
    model = Vote

    def read(self, request, id, *args, **kwargs):
        """Return the different vote counts for an issue

        example output:

        {"-1": 1, "1":10, "10": 1  ... }

        This Means for -1, (against) there is 1 vote
        , 10 people voted for (1) and 1 person voted blank (10) *unconvincing*
        Here are all the different votes directions:

        -1.  "Against",

        1.   "For",

        *blank_votes* note always higer than 10.

        content related problems with issues

        10.  'Unconvincing',
        11.  'Not political',
        12.  'Can\'t completely agree',

        form related problems with issues

        13.  "Needs more work",
        14.  "Badly worded",
        15.  "Duplicate",
        16.  'Unrelated source',

        personal considerations

        17.  'I need to know more',
        18.  'Ask me later',
        19.  'Too personal',

        """
        try:
            issue = Issue.objects.get(id=id)
        except Issue.DoesNotExist:
            return rc.NOT_HERE

        votes = Vote.objects.get_for_object(issue)
        return votes

    @classmethod
    def vote(cls, vote):
        return vote[0]

    @classmethod
    def vote_count(cls, vote):
        return vote[1]

    @staticmethod
    def resource_uri():
        return ('api_issue_votes', ['id'])


class IssueList(AnonymousBaseHandler):
    """Resource for Listings of issues in a particular order

    - 'new'
    - 'popular'
    - 'controversial'
    """
    allowed_methods = ('GET', )

    def read(self, request, **kwargs):
        """ get listing of issue uri's """

        sortorder = kwargs.get("sortorder", "")
        if sortorder == 'popular':
            qs = Vote.objects.get_popular(Issue)
            qs = qs.values_list('object_id' , 'totalvotes')
        elif sortorder == 'controversial':
            qs = Vote.objects.get_controversial(Issue)
            qs = qs.values_list('object_id' , 'avg')
        elif sortorder == 'new':
            qs = Issue.objects.all().order_by('-time_stamp')
            qs = qs.values_list('id', 'time_stamp')
        else:
            return rc.BAD_REQUEST
        page = paginate(request, qs, **kwargs)
        result = []
        for id_value in page.object_list:
            uri = self.issue_url(id_value)
            result.append((uri, id_value[1]))
        return result

    # not no classmethods because query returns list of tuples.
    # and the responder will not look at those.
    def issue_url(cls, id_value):
        return reverse('api_issue', args=[id_value[0]])


class VoteHandler(BaseHandler):
    """Read and Post votes for user.
    """
    allowed_methods = ('GET', 'POST', )
    fields = ('vote', 'time_stamp', 'issue_uri', 'keep_private', )
    model = Vote

    def read(self, request, id=None, **kwargs):
        """
        Returns the votes for an user.
        """
        ctype = ContentType.objects.get_for_model(Issue)
        queryset = self.model.objects.filter(user = request.user,
                        content_type = ctype.pk).order_by('time_stamp')
        queryset = queryset.filter( is_archived=False )
        if id:
            queryset = queryset.filter(object_id=id)
        queryset.order_by("username")
        page = paginate(request, queryset, **kwargs)
        return page.object_list

    @classmethod
    def issue_uri(cls, vote):
        return "%s" % reverse('api_issue', args=[vote.object_id])

    @validate(VoteForm)
    def create(self, request):
        """
        Vote on an Issue

        postparameters:

        - object_id
        - vote
        - keep_private (optional)

        """
        ctype = ContentType.objects.get_for_model(Issue)
        attrs = self.flatten_dict(request.POST)
        object_id = attrs.pop('issue')
        attrs.update({'content_type': ctype,
                       'object_id': object_id,
                       'is_archived': False,
                })

        if self.exists(**attrs):
            logging.debug("conflict")
            logging.debug(attrs)
            return rc.DUPLICATE_ENTRY
        if not 'keep_private' in attrs:
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
    allowed_methods = ('GET', )
    fields = ('username', 'score', 'ranking', )
    model = User

    def read(self, request, id=None, *args, **kwargs):
        if id:
            try:
                return User.objects.filter(id=id)
            except User.DoesNotExist:
                return rc.NOT_FOUND
        else:
            queryset = User.objects.filter().order_by('username')
            page = paginate(request, queryset, **kwargs)
            return page.object_list

    @classmethod
    def score(cls, user):
        return  get_profile_field(user, 'score', 0)

    @classmethod
    def ranking(cls, user):
        score = cls.score(user)
        return UserProfile.objects.filter(score__gte = score).count()

    #TODO GRAVATAR url !!
    @staticmethod
    def resource_uri():
        return ('api_user', ['id'])


class UserHandler(BaseHandler):
    """Get User Details for authenticated user
    """
    allowed_methods = ('GET', )
    fields = ('username', 'firstname', 'lastname', 'email', 'score',
            'ranking', 'role')
    anonymous = AnonymousUserHandler
    model = User

    def read(self, request, *args, **kwargs):
        return request.user

    @classmethod
    def score(cls, user):
        return get_profile_field(user, 'score', 0)

    @classmethod
    def role(cls, user):
        return get_profile_field(user, 'role', 'citizen')

    @classmethod
    def ranking(cls, user):
        score = cls.score(user)
        return UserProfile.objects.filter(score__gte = score).count()

    @staticmethod
    def resource_uri():
        return ('api_user', ['id'])


class AnonymousIssueHandler(AnonymousBaseHandler):

    fields = ('title', 'body', ('user', ('username', )), 'time_stamp',
            'source_type', 'url')
    model = Issue

    def read(self, request, id=None, *args, **kwargs):
        if id:
            try:
                return self.model.objects.get(id=id)
            except ObjectDoesNotExist:
                return rc.NOT_FOUND
        else:
            queryset = self.model.objects.order_by('-time_stamp')
            page = paginate(request, queryset, **kwargs)
            return page.object_list

    @staticmethod
    def resource_uri():
        return ('api_issue', ['id'])


class IssueHandler(BaseHandler):
    allowed_methods = ('GET', 'POST')
    anonymous = AnonymousIssueHandler
    fields = ('title', 'body', ('user', ('username')), 'time_stamp',
            'souce_type', 'url')
    model = Issue

    def read(self, request):
        return self.anonymous.read(request)

    @validate(IssueForm)
    def create(self, request):
        """Create new issue

        post parameters:

        - title
        - body
        - direction ( vote of the user )
        - url
        - source_type
        - is_draf
        """
        attrs = self.flatten_dict(request.POST)
        issue = gamelogic.actions.propose(
            request.user,
            attrs['title'],
            attrs['body'],
            int(attrs['direction']),
            attrs['url'],
            attrs['source_type'],
            attrs['is_draft'],
            )
        if issue:
            return rc.CREATED
        else:
            return rc.BAD_REQUEST

    @staticmethod
    def resource_uri():
        return ('api_issue', ['id'])


class AnonymousMultiplyHandler(AnonymousBaseHandler):
    allowed_methods = ('GET', )
    model = MultiplyIssue

    fields = (('user', ('resource_uri')), 'time_stamp',
            ('issue', ('resource_uri')))

    def read(self, request, id=None, *args, **kwargs):
        """ Read the active multiplies for specific issue
            or all multiplies in decending paginated order
        """
        if id:
            return self.model.objects.filter(issue=id)
        else:
            queryset = self.model.objects.all().order_by('-time_stamp')
            page = paginate(request, queryset, **kwargs)
            return page.object_list

    @staticmethod
    def resource_uri():
        return ('api_multiply', ['id'])


class MultiplyHandler(BaseHandler):
    """If a user has enough game points the user can multiply the value of an issue.
    A multiplied issue will make it more important and gives generate more points.(XXX not yet implemented)
    """
    allowed_methods = ('POST', 'GET')
    anonymous = AnonymousMultiplyHandler
    model = MultiplyIssue
    fields = (('user', ('resource_uri')), 'time_stamp', ('issue',
        ('resource_uri')))

    #No def read, default behaviour is what we want.
    @validate(MultiplyForm)
    def create(self, request):
        """ expects an issue id and optional a downgrade boolean
            in the POST data
        """
        attrs = self.flatten_dict(request.POST)

        issue = gamelogic.actions.multiply(
            request.user,
            Issue.objects.get(id = attrs['issue']),
            attrs.get('downgrade', False),
        )
        if issue:
            return rc.CREATED
        else:
            return rc.FORBIDDEN

    @staticmethod
    def resource_uri():
        return ('api_multiply', ['id'])


class TagCloudHandler(BaseHandler):
    allowed_methods = ('GET', )
    fields = ('name','count','font_size')
        
    def read (self, request):
        """
        Reads the Tag Cloud for all posts
        """
        tags = Tag.objects.usage_for_model(Issue, counts=True)
        return calculate_cloud(tags)

class TagHandler(BaseHandler):
    allow_methods = ('GET',)
    #model = FeedItem
    #fields = ('title', 'link', 'summary', 'tags')
        
    def read(self, request, tags=None, **kwargs):
        """Read posts. Optional parameters:

        tags -- return issues that have the specified tags
        
        """

        if tags == None and 'tags' in request.GET:
            tags = request.GET['tags']

        tags = [ tags ]    

        if tags:
            issues = TaggedItem.objects.get_by_model(Issue, tags)
            print issues
        else: 
            issues = [] 
        page = paginate(request, issues, **kwargs)
        result = []
        for issue in page.object_list:
            uri = self.issue_url(issue.id)
            result.append((uri))
        return result

    def create(self, request, **kwargs):
        """
        XXX not yet implemented
        tag an issue

        Examples:

        ====================== ======================================= ================================================
        Tag input string       Resulting tags                          Notes
        ====================== ======================================= ================================================
        apple ball cat         [``apple``], [``ball``], [``cat``]      No commas, so space delimited
        apple, ball cat        [``apple``], [``ball cat``]             Comma present, so comma delimited
        "apple, ball" cat dog  [``apple, ball``], [``cat``], [``dog``] All commas are quoted, so space delimited
        "apple, ball", cat dog [``apple, ball``], [``cat dog``]        Contains an unquoted comma, so comma delimited
        apple "ball cat" dog   [``apple``], [``ball cat``], [``dog``]  No commas, so space delimited
        "apple" "ball dog      [``apple``], [``ball``], [``dog``]      Unclosed double quote is ignored
        ====================== ======================================= ================================================
        """

    # no classmethods because query returns list of tuples.
    # and the responder will not look at those.
    def issue_url(cls, id):
        return reverse('api_issue', args=[id])


def get_profile(user):
    try:
        return user.get_profile()
    except UserProfile.DoesNotExist:
        pass

def get_profile_field(user, attribute, default):
    profile = get_profile(user)
    if not profile:
        return default
    if hasattr(profile, attribute):
            return getattr(profile, attribute)
    return default
