"""

provide xhr methods to get information on game progress.

"""

from django.http import HttpResponse
from django.utils import simplejson

from issue.models import Issue
from voting.models import Vote
from voting.vote_types import normal_votes 
from profiles.models import UserProfile

def json_error_response(error_message):
    return HttpResponse(simplejson.dumps(dict(success=False,
                                      error_message=error_message)))


def xhr_key_data(request):
    """ get json data for key in GET 
    
        possible keys

        user
        folowers
        tag_tagname
        stats
        
    """
    if request.method == 'POST':
        return json_error_response(
            'XMLHttpRequest votes can only be made using GET.')
 
    key = request.GET.get('key', False)

    if not key:
        return json_error_response('No key provided.')

    data = {}

    if key == 'user':
        # provide user data of votes.
        # dict of ids.
        if not request.user.is_authenticated():
            data['votes'] = request.session.get("vote_history", {})
        else:
            queryset = Vote.objects.get_user_votes(request.user, Issue)
            queryset = queryset.filter(direction__in=normal_votes.keys())
            votes = queryset.values_list('object_id', 'direction',)
            votes = dict([(object_id, direction) for object_id, direction in votes ])
            data = {'votes' : votes }

    elif key == 'followers':
        #TODO
        pass
        # provide public issue keys of user.
    elif key == 'tags':
        pass
        # find tags on Issues.
        # return list of tags with ids.

    elif key.startswith('tag'):
        tag = key[4:]
        stag = "\"%s\"" % tag 
        issues = Issue.tagged.with_any(stag)
        issues = issues.filter(is_draft=False)
        issues = issues.values_list('id',) 
        issues = [ i[0] for i in issues]
        data = { key : issues }
    elif key == 'parties':
        parties = UserProfile.objects.filter(role='party program');
        parties.select_related()
        names = []

        for profile in parties:
            name = profile.user.username
            profile_issues = Issue.active.filter(user=profile.user)
            ids = [issue.id for issue in profile_issues]
            if len(ids) > 3:
                data[name] = ids
                names.append(name)
            
        data['names'] = names 

    elif key == 'issues':
        issues = Issue.active.all();    
        ids = [issue.id for issue in issues]
        data['issues'] = ids

    elif key == 'stats':
        #TODO
        # provide statistics.
        pass
    else:
        return json_error_response('Invalid key provided.')

    data['succes'] = True
    return HttpResponse(simplejson.dumps(data))

