from fabric.api import * 

env.user = 'democracy'
env.hosts = ['derdekamer.net',]

def prepare_deploy():
    local('./TESTS', capture=True)
    local('git push ch stephan:deployment', capture=False)


def restart_server():
    run('./init/democracy restart') 


def update():
    prepare_deploy()
    with cd('democracy'):
        run('git checkout -f')
    restart_server()
