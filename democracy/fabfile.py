from fabric.api import * 

env.user = 'democracy'
env.hosts = ['derdekamer.net',]

def push_deploy():
    local('git push ch stephan:deployment', capture=False)

def test():
    result = local('python manage.py test tests --settings=voting.tests.settings ', capture=False)
    if result.failed:
        abort("Aborting tests failed")
    result = local('python manage.py test --settings=testsettings', capture=False)
    if result.failed:
        abort("Aborting voting tests failed")
    print "tests seemed to be ok!"

def restart_server():
    run('./init/democracy restart') 


def updatelanguagefiles():
    with cd('democracy/democracy/'):
        run('git commit locale/ -m "update language files"')
    local('git pull ch deployment', capture=True)

def update():
    test()
    push_deploy()
    with cd('democracy'):
        run('git checkout -f')
    with cd('democracy/democracy/'):
        run('python manage.py compilemessages')
    restart_server()
