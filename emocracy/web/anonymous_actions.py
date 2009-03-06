def vote(request, issue, vote_int):
    # TODO move this to a more appropriate module. (something like anonymous.py)
    """This function lets anonymous users vote, votes are stored in the session
    as key:value pairs."""
    try:
        request.session["vote_history"][issue.pk] = vote_int
    except KeyError:
        request.session["vote_history"] = {issue.pk : vote_int}
    request.session.modified = True
