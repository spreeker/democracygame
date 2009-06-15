import datetime

from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse

from django.db.models import Q
from piston.handler import BaseHandler, AnonymousBaseHandler
from piston.utils import rc

from emocracy.issues_content.models import IssueBody
from emocracy.voting.models import Issue
from emocracy.voting.models import Vote

import gamelogic.actions

domain = Site.objects.get_current().domain

class AnonymousVoteHandler(AnonymousBaseHandler):
    allowed_methods = ('GET',)
    fields = ('vote', 'time_stamp', 'issue_uri', 'keep_private', 'user_uri')
    #model = Vote

    def read(self, request, id, *args, **kwargs):
        return self.model.objects.filter(issue=id)

    @classmethod
    def issue_uri(cls, vote):
        return "http://%s%s" %(domain, reverse('api_issue' , args=[vote.issue.id]))
    
    @classmethod
    def user_uri(cls, vote):
        return "http://%s%s" %(domain , reverse('api_user' , args=[vote.owner.id]))

class AnonymousVoteListHandler(AnonymousVoteHandler):
    allowed_methods = ('GET',)
    fields = ('vote', 'time_stamp', 'issue_uri', 'keep_private', 'user_uri')
    model = Vote

    def read(self, request, *args, **kwargs):
        return self.model.objects.filter()

class VoteHandler(BaseHandler):
    allowed_methods = ('GET',)
    fields = ('vote', 'time_stamp', 'issue_uri', 'keep_private', 'user_uri')
    model = Vote
    #anonymous = AnonymousVoteHandler

    def read(self, request, id, *args, **kwargs):
        return self.model.objects.filter(issue=id)

    @classmethod
    def issue_uri(cls, vote):
        return "http://%s%s" % (domain , reverse('api_issue' , args=[vote.issue.id]))
    
    @classmethod
    def user_uri(cls, vote):
        return "http://%s%s" %(domain , reverse('api_user' , args=[vote.owner.id]))


class VoteListHandler(VoteHandler):
    allowed_methods = ('GET', 'POST',)
    fields = ('vote', 'time_stamp', 'issue_uri', 'keep_private', 'user_uri')
    model = Vote
    anonymous = AnonymousVoteListHandler

    def read(self, request, *args, **kwargs):
        return self.model.objects.filter()

    def create(self, request):
        attrs = self.flatten_dict(request.POST)
        attrs['is_archived'] = False
        attrs['owner'] = request.user.id

        if self.exists(**attrs):
            return rc.DUPLICATE_ENTRY
        else:
            current = Vote.objects.filter(
                Q(issue=attrs['issue']) &
                Q(owner=request.user) &
                Q(is_archived=False)
            )
            if len(current) == 0:
                pass
            else:
                current = current[0]
                current.is_archived = True
                current.save()
            vote = Vote(vote=attrs['vote'], 
                            issue=Issue.objects.get(id=attrs['issue']),
                            keep_private=attrs['keep_private'],
                            owner=request.user,
                            time_stamp = datetime.datetime.now())
            vote.save()
            
            return vote

class AnonymousUserListHandler(AnonymousBaseHandler):
    allowed_methods = ('GET',)
    fields = ('user_uri', 'username')
    exclude = ('absolute_uri',)
    model = User

    def read(self, request, *args, **kwargs):
        return self.model.objects.filter()

    @classmethod
    def user_uri(cls, user):
        pass
        return "http://%s%s" % (domain , reverse('api_user' , args=[user.id]))
    

class UserListHandler(BaseHandler):
    allowed_methods = ('GET',)
    fields = ('user_uri', 'username')
    anonymous = AnonymousUserListHandler
    model = User

    def read(self, request, *args, **kwargs):
        return self.model.objects.filter()

    @classmethod
    def user_uri(cls, user):
        return "http://%s%s" % (domain , reverse('api_user' , args=[user.id]))
    

class AnonymousUserHandler(AnonymousBaseHandler):
    allowed_methods = ('GET',)
    fields = ('username', 'score', 'user_uri')
    #model = User

    def read(self, request, id, *args, **kwargs):
        return self.model.objects.filter(id=id)

    @classmethod
    def score(cls, user):
        return user.get_profile().score

    @classmethod
    def user_uri(cls, user):
        return "http://%s%s" % (domain , reverse('api_user' , args=[user.id]))
    

class UserHandler(BaseHandler):
    allowed_methods = ('GET',)
    fields = ('username', 'score', 'user_uri')
    anonymous = AnonymousUserHandler
    #model = User

    def read(self, request, id, *args, **kwargs):
        return self.model.objects.filter(id=id)
    
    @classmethod
    def score(cls, user):
        return user.get_profile().score
    
    @classmethod
    def user_uri(cls, user):
        return "http://%s%s" % (domain , reverse('api_user' , args=[user.id]))
    

class AnonymousIssueListHandler(AnonymousBaseHandler):
    allowed_methods = ('GET',)
    fields = ('issue_uri', 'title', 'body', ('owner', ('username', 'user_uri',)), 'time_stamp', 'souce_type', 'url', 'votes_for', 'votes_abstain', 'votes_against')
    model = IssueBody

    def read(self, request, *args, **kwargs):
        return self.model.objects.filter()

    @classmethod
    def votes_for(cls, issue):
        return Vote.objects.filter(Q(issue=issue) & Q(vote=1) & Q(is_archived=False)).count()

    @classmethod
    def votes_abstain(cls, issue):
        return Vote.objects.filter(Q(issue=issue) & Q(vote__gt=9) & Q(is_archived=False)).count()
    
    @classmethod
    def votes_against(cls, issue):
        votes_against = Vote.objects.filter(Q(issue=issue) & Q(vote=-1) &Q(is_archived=False)).count()
        return votes_against
    
    @classmethod
    def user_uri(cls, user):
        return "http://%s%s" % (domain , reverse('api_user' , args=[user.id]))
    
    
    @classmethod
    def issue_uri(cls, issue):
        return "http://%s%s" % (domain , reverse('api_issue' , args=[issue.id]))
        
class IssueListHandler(BaseHandler):
    allowed_methods = ('GET',)

    anonymous = AnonymousIssueListHandler
    fields = ('issue_uri', 'title', 'body', ('owner', ('username', 'user_uri',)), 'time_stamp', 'souce_type', 'url', 'votes_for', 'votes_abstain', 'votes_against', 'my_vote')
    model = IssueBody
    
    def read(self, request, *args, **kwargs):

        issues= self.model.objects.filter()
        issue_list = []
        for issue in issues:
            vote = Vote.objects.filter(Q(issue=issue) & Q(owner=request.user) &Q(is_archived=False))
            issue.my_vote = vote
            issue_list.append(issue)
        return issue_list

    @classmethod
    def my_vote(cls, issue):
        return issue.my_vote

    @classmethod
    def votes_for(cls, issue):
        return Vote.objects.filter(Q(issue=issue) & Q(vote=1) &Q(is_archived=False)).count()

    @classmethod
    def votes_abstain(cls, issue):
        votes_abstain = Vote.objects.filter(Q(issue=issue) & Q(vote__gt=9) &Q(is_archived=False)).count()
        return votes_abstain

    @classmethod
    def votes_against(cls, issue):
        votes_against = Vote.objects.filter(Q(issue=issue) & Q(vote=-1) &Q(is_archived=False)).count()
        return votes_against

    @classmethod
    def user_uri(cls, user):
        return "http://%s%s" % (domain , reverse('api_user' , args=[user.id]))
        

    @classmethod
    def issue_uri(cls, issue):
        return "http://%s%s" % (domain , reverse('api_issue' , args=[issue.id]))
        

class AnonymousIssueHandler(AnonymousBaseHandler):
    allowed_methods = ('GET',)
    fields = ('issue_uri', 'title', 'body', ('owner', ('username', 'user_uri',)), 'time_stamp', 'source_type', 'url')
    #model = IssueBody

    def read(self, request, id, *args, **kwargs):
        return self.model.objects.filter(id=id)

    @classmethod
    def user_uri(cls, user):
        return "http://%s%s" % (domain , reverse('api_issue' , args=[issue.id]))
        

    @classmethod
    def issue_uri(cls, issue):
        return "http://%s%s" % (domain , reverse('api_issue' , args=[issue.id]))
        

class IssueHandler(BaseHandler):
    allowed_methods = ('GET', 'POST',)
    anonymous = AnonymousIssueHandler
    fields = ('issue_uri', 'title', 'body', ('owner', ('username', 'user_uri',)), 'time_stamp', 'souce_type', 'url')
    #model = IssueBody
        
    def create(self, request):
        attrs = self.flatten_dict(request.POST)

        if self.exists(**attrs):
            return rc.DUPLICATE_ENTRY
        else:
            issue = gamelogic.actions.propose(
                request.user,
                attrs['title'],
                attrs['body'],
                attrs['owners_vote'],
                attrs['url'],
                attrs['source_type'],
                attrs['is_draft'],
                None,
            )
            issue.save()
            return issue
    
    def read(self, request, id):
        if id==None:
            return self.model.objects.filter()
        else:
            return self.model.objects.filter(id=id)
    
    @classmethod
    def user_uri(cls, user):
        return "http://%s%s" % (domain , reverse('api_user' , args=[user.id]))

    @classmethod
    def issue_uri(cls, issue):
        return "http://%s%s" % (domain , reverse('api_issue' , args=[issue.id]))
