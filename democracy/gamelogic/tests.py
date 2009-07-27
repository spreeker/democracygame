from gamelogic import levels
from gamelogic import actions 
from gamelogic import score
from gamelogic.models import MultiplyIssue
from profiles.models import UserProfile
from issue.models import Issue
from voting.models import Vote

from django.contrib.auth.models import User
from django.db import transaction
from django.test import TestCase 


class TestUsers(TestCase):
    usernames = ['test1', 'test2','test3']
    profiles = [] 
    users = [] 
    
    def setUp(self):
        self.load_users() # loads users from DB or creates them
        levels.MIN_SCORE_ACTIVE_CITIZENS = 10
        levels.MAX_OPINION_LEADERS = 2
        score.PROPOSE_SCORE = 2
        score.PROPOSE_VOTE_SCORE = 1

    def tearDonw(self):
        User.objects.delete()        

    def __str__(self):
        data = " User Profile.role  score \n "
        for i,u in enumerate(self.users):
            p = self.profiles[i]
            data += "%15s %15s %4d" % ( u.username , p.role , p.score )
            data += "\n"

        return data
     
    def load_users(self):
        self.users = []
        self.profiles = []

        for user in self.usernames:
            
            u = self.get_user( user ) 
            p = self.get_profile ( u ) 

            self.users.append(u)
            self.profiles.append( u.get_profile()) 

    def get_user(self ,  name ):
        try:
            user = User.objects.get( username = name )
        except User.DoesNotExist :
            user = User.objects.create_user( name , '%s@example.com' % name  , 'testpw' )
        return user

    def get_profile (self , user ):
        try:
            profile = UserProfile.objects.get( user = user ) 
        except UserProfile.DoesNotExist :
            profile = UserProfile.objects.create( user = user , score = 0 , role = 'citizen' )
        return profile 

    def reset(self , score = 0 , role = "citizen" ):
        """ set all users on score and role 
        """
        for p in self.profiles:
            p.score = score
            p.role = role 
            p.save()


class TestLeveling(TestUsers):
    """ test the leveling aka role change of users """

    def test_create_op(self):
        self.reset()

        levels.change_score( self.profiles[0] , 11 )    
        self.load_users()
        self.assertEqual( self.profiles[0].role , 'opinion leader' )

    def test_create2_op(self):
        """ create 2 opinion leaders
        """
        self.test_create_op()

        levels.change_score( self.profiles[1] , 12 )
        self.load_users()
        self.assertEqual( self.profiles[0].role , 'opinion leader' )
        self.assertEqual( self.profiles[1].role , 'opinion leader' )

    def test_swap_leaders(self):
        self.test_create2_op()
        # now a 3rd opinion leader cannot be created
        # so now p3 becomes active citizen
        self.profiles[2].score = 0
        levels.change_score( self.profiles[2] , 11 )
        self.assertEqual( self.profiles[2].role , 'active citizen' )
        levels.change_score( self.profiles[2] , +2 )
        #now t3 has highest score and will be opinion leader
        self.assertEqual( self.profiles[2].role , 'opinion leader' )
        # this is still true because we still have to reload from the database        
        self.assertEqual( self.profiles[0].role , 'opinion leader' )
        # reload  to see the correct value
        self.load_users()
        self.assertEqual( self.profiles[0].role , 'active citizen' )

    def test_down_grade(self):
        for p in self.profiles:
            p.score = 33
            p.role = "opinion leader"
            p.save()

        levels.change_score( self.profiles[0] , - self.profiles[0].score + 1 )
        self.load_users()
        self.assertEqual( self.profiles[0].role , 'citizen')

        self.profiles[0].score = 11
        self.profiles[0].role = 'opinion leader'
        self.profiles[0].save()

        levels.change_score( self.profiles[0] , 1 )
        # now profile 0  should be downgraded to active citizen again
        self.load_users()
        # first p0 will be opl because there are not enough.
        self.assertEqual( self.profiles[0].role , 'opinion leader')
        levels.change_score( self.profiles[2] , 1 )
        self.load_users()
        # now p3 will be opl and p1 active citizen
        self.assertEqual( self.profiles[2].role , 'opinion leader')
        self.assertEqual( self.profiles[0].role , 'active citizen' )

class TestActionData(TestUsers):
    """ 
    We need testdata like issues and multiplies to vote on 
    and do other actions with
    """

    issues = [ "issue1", "issue2", "issue3" ]

    def setUp(self):
        super(TestActionData, self).setUp()

        self.reset( levels.MIN_SCORE_ACTIVE_CITIZENS, "active citizen" )
        self.load_users()
        # make sure default values in db are now ok
        self.assertEqual( User.objects.count() , 3 )
        self.assertEqual( self.profiles[0].score , levels.MIN_SCORE_ACTIVE_CITIZENS )
        
        # add issues
        for i, issue in enumerate(self.issues):
            actions.propose(self.users[i] , issue , 10*issue , 1 , "example.com" , "website" )

        # test the adding of issues was succesfull
        # this get run multiple times , dubplicate issues should not be created
        self.assertEqual( Issue.objects.count() , len(self.issues))

    def tearDown(self):
        super(TestActionData, self).tearDown()

        qs = Issue.objects.filter( title__startswith="issue" )
        qs.delete()
        Vote.objects.all().delete()
        MultiplyIssue.objects.all().delete()

    def do_vote(self, user, issue, vote ):
        profile = user.get_profile()
        vote_func = actions.role_to_actions[profile.role]['vote']
        vote_func(user, issue, vote, False) 

    def do_multiply(self , user , issue ):
        # only Opinion leaders can multiply 
        try :
            actions.role_to_actions[self.profiles[2].role]['multiply']
            self.fail(" %s %s is able to Multiply " % (self.users[2].username , self.profiles[2].role ))
        except KeyError :
            pass

        multiply_func = actions.role_to_actions[self.profiles[0].role]['multiply']

        multiply_func(user, issue)


class TestActions(TestActionData):
    """ test all different actions a user can do """

    def test_vote(self):
        # in the test setup we define 3 issues. 
        # and an issue user also votes on it.
        # 3 issues is 3 default votes

        issue1 = Issue.objects.get(title="issue1")  
        issue2 = Issue.objects.get(title="issue2")  

        self.do_vote(self.users[0], issue2, 1 )

        self.load_users() 
        delta = score.PROPOSE_SCORE + levels.MIN_SCORE_ACTIVE_CITIZENS 
        # check if score has changed after vote
        self.assertEqual( self.profiles[0].score - delta, score.VOTE_SCORE )
        # check if identical repeated vote on own issue changes nothing
        self.do_vote( self.users[0], issue1, 1 ) 
        self.load_users() 
        self.assertEqual( self.profiles[0].score - delta, score.VOTE_SCORE )

        self.do_vote( self.users[0], issue2 , 1 ) 
        # score should stay the same
        self.assertEqual( self.profiles[0].score - delta, score.VOTE_SCORE )

        # check if different vote gets into the database
        allVotes = Vote.objects.all().count()
        self.assertEqual( allVotes, 4 )

        # now we change our mind a lot. this should result in no extra point and just 1 extra vote
        # in the database
        self.do_vote( self.users[0], issue2, -1 ) 
        self.do_vote( self.users[0], issue2, -1 ) 
        self.do_vote( self.users[0], issue1, 1 ) 

        self.load_users() 
        self.assertEqual( self.profiles[0].score - delta , score.VOTE_SCORE )
        allVotes = Vote.objects.all().count()
        self.assertEqual( allVotes, 5 )

    def test_multiply(self):
               
        issue = Issue.objects.get( title = "issue2" )

        self.do_multiply( self.users[0] , issue )

        # do a multiply on issue
        count_multiplies = MultiplyIssue.objects.filter( issue = issue ).count()
        self.assertEqual( count_multiplies , 1 ) 
        # do too many multiplies on issue
        import gamelogic.models
        maxM = gamelogic.models.MAX_MULTIPLIERS
        for x in range(maxM + 10 ):
            self.do_multiply( self.users[0] , issue ) 

        count_multiplies = MultiplyIssue.objects.filter( issue = issue ).count()
        self.assertEqual( count_multiplies , maxM )
        
