from psycopg2 import IntegrityError
from emocracy.gamelogic import levels
from emocracy.gamelogic import actions 
from emocracy.gamelogic import score
from emocracy.profiles.models import UserProfile
from emocracy.voting.models import Issue

from django.contrib.auth.models import User
from django.db import transaction

import unittest

def safe_sql(Model , **cargs ):
    """ if something goes wrong i can rollback changes.
        needed if you test code on exciting postgress database
        for normal testpurposes it overkill because those work on
        an empty database.
    """
    try:
        sid = transaction.savepoint()
        instance = Model( cargs )
        transaction.savepoint_commit(sid)
        instance.save()
        return instance 
    except IntegrityError :
        transaction.savepoint_rollback(sid)
        return Model.objects.get( gargs )


class TestUsers(unittest.TestCase):
    usernames = ['test1' , 'test2' ,'test3' ]
    profiles = [] 
    users = [] 
    
    def setUp(self):
        self.load_users()
        levels.MIN_SCORE_ACTIVE_CITIZENS = 10
        levels.MAX_OPINION_LEADERS = 2

    def __str__(self):
        data = " TestUsers Profile score and role change \n"
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
            sid = transaction.savepoint()
            user = User.objects.create_user( name , '%s@example.com' % name  , 'testpw' )
            transaction.savepoint_commit(sid)
            return user
        except IntegrityError :
            transaction.savepoint_rollback(sid)
            user = User.objects.get( username = name )
            return user

    def get_profile (self , user ):
        try:
            sid = transaction.savepoint()
            profile = UserProfile.objects.create( user = user , score = 0 , role = 'citizen' )
            transaction.savepoint_commit(sid)
            return profile
        except IntegrityError :
            transaction.savepoint_rollback(sid)
            profile = UserProfile.objects.get( user = user ) 
            return profile 

    def cleanup(self):
        for user in users:
            user.delete()

    def reset(self , score = 0 , role = "citizen" ):
        """ set all users on score and role 
        """
        for p in self.profiles:
            p.score = score
            p.role = role 
            p.save()

    def runTest(self):
        pass


class TestLeveling(TestUsers):
    """ test the leveling aka role change of users """


    def test_create_op(self):
        self.reset()

        levels.change_score( self.profiles[0] , 11 )    
        self.load_users()
        self.assertEqual( self.profiles[0].role , 'opinion leader' )

    def test_create2_op(self):
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

class TestActions(TestUsers):
    """ test all different actions a user can do """

    issues = [ "issue1" , "issue2" , "issue3" ]

    def setUp(self):
        """ we need issues to vote on and do other actions with
        """
        super(TestActions , self).setUp()
        self.reset( levels.MIN_SCORE_ACTIVE_CITIZENS , "active citizen" )
        self.load_users()
        # made sure default values in db are now ok
        self.assertEqual( User.objects.count() , 3 )
        self.assertEqual( self.profiles[0].score , levels.MIN_SCORE_ACTIVE_CITIZENS )
        
        # add issues
        for i , issue in enumerate(self.issues):
            actions.propose(self.users[i] , issue , 10*issue , 1 , "example.com" , "url" )


        # test the adding of issues was succesfull
        # this get run multiple times , dubplicate issues should not be created
        self.assertEqual( Issue.objects.count() , len(self.issues))
        
    def test_vote(self):

        issue = Issue.objects.get( title = "issue2" )  

        vote_func = actions.role_to_actions[self.profiles[0].role]['vote'] 
        vote_func( self.users[0] , issue , 1 , False) 
        self.load_users()
        delta = score.PROPOSE_SCORE + levels.MIN_SCORE_ACTIVE_CITIZENS
        self.assertEqual( self.profiles[0].score - delta , score.VOTE_SCORE )

    def test_multiply(self):
        # only Opinion leaders can multiply 
        try :
            actions.role_to_actions[self.profiles[2].role]['multiply']
            self.fail(" %s %s should not be able to Multiply " % (self.users[2].username , self.profiles[2].role ))
        except KeyError :
            pass

    def test_tag(self):
        pass

    def tearDown(self):
        qs = Issue.objects.filter( title__startswith = "issue" )
        qs.delete()

"""
tu.= TestUsers()
tu.setUp()

print "initial user data"
print tu

levels.NUMBER_OF_OPINION_LEADERS = 2
levels.MIN_SCORE_ACTIVE_CITIZENS = 10 

levels.change_score( tu.profiles[0] , 11 )
print "citizen to opinion leader"
print tu

print "test2 to opinion leader"
levels.change_score( tu.profiles[1] , 12 )
print tu
print "but we have to reload users from db to see correct results"
tu.load_users()
print tu

# now a 3rd opinion leader cannot be created
# so now p3 becomes active citizen
levels.change_score( tu.profiles[2] , 11 )
tu.load_users()
print tu.

#  now we give p3 the highest score!
levels.change_score( tu.profiles[2] , +2 )

tu.load_users()
print tu

qs = UserProfile.objects.filter(user__username__startswith = 'test')
 # this should print out the same
for p in qs:
    print "%15s %15s %4d" % (p.user.username , p.role , p.score)
    u = p.user
    p.delete()
    u.delete()
"""
