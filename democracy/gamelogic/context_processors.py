from gamelogic.actions import get_actions 

def actions(request):
    possible_actions = get_actions(request.user)
    return {'actions' : possible_actions }
