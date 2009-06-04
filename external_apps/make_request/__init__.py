# coding: utf-8
import collections
import httplib
import logging
from urlparse import urlparse
from urlencoding import parse_qs, compose_qs


def prepare_request(url, method='GET', content=None, headers={}):
    """
    This is the generic processing logic used by the various APIs.

    If content is a Mapping object, parameters will be processed. In this case,
    query parameters from the URL will be processed and merged with the content
    dict. They will then be appended to the URL or sent as the body based on
    the method.

    Arguments:

        `url`
            The URL - query parameters will be parsed out.

        `method`
            The HTTP method to use.

        `content`
            A dict of key/values or string/unicode value.

        `headers`
            A dict of headers.

    """
    # we potentially modify them
    headers = headers.copy()

    parts = urlparse(url)
    url = parts.path
    if parts.params:
        url += ';' + parts.params

    # we dont do much with the url/body unless content is a Mapping object
    if isinstance(content, collections.Mapping):
        # merge the parameters in the query string
        if parts.query:
            qs_params = parse_qs(parts.query)
            qs_params.update(content)
            content = qs_params

        # put the content in the url or convert to string body
        if content:
            content = compose_qs(content)
            if method in ('HEAD', 'GET'):
                url += '?' + content
                content = None
            else:
                if 'Content-Type' not in headers:
                    headers['Content-Type'] = 'application/x-www-form-urlencoded'
    else:
        if parts.query:
            url += '?' + parts.query

    # add Content-Length if needed
    if content and 'Content-Length' not in headers:
        headers['Content-Length'] = len(content)

    return {
        'scheme': parts.scheme,
        'netloc': parts.netloc,
        'url': url,
        'method': method,
        'content': content,
        'headers': headers,
    }

def make_request(*args, **kwargs):
    """
    Make HTTP requests.

    >>> import json
    >>> BASE_URL = 'http://localhost:6666/echo'
    >>> BASE_URL = 'http://json-service.appspot.com/echo'

    Default GET with a simple URL containing the query parameters:
    >>> response = make_request(BASE_URL + '/more/path?a=1')
    >>> response.status
    200
    >>> j = json.loads(response.read())
    >>> j['method']
    u'GET'
    >>> j['path']
    u'/echo/more/path'
    >>> j['query_params']
    {u'a': u'1'}


    POST request with array value using parameters.
    >>> response = make_request(BASE_URL, 'POST', {'a':1, 'b': [2,3]})
    >>> response.status
    200
    >>> j = json.loads(response.read())
    >>> j['method']
    u'POST'
    >>> j['path']
    u'/echo'
    >>> j['query_params']
    {}
    >>> j['post_params']
    {u'a': u'1', u'b': [u'2', u'3']}

    Raw Content Body with POST request:
    >>> response = make_request(BASE_URL, 'POST', u'xXyYzZ', {'Content-Type': 'text/plain'})
    >>> response.status
    200
    >>> j = json.loads(response.read())
    >>> j['method']
    u'POST'
    >>> j['body']
    u'xXyYzZ'

    """
    opts = prepare_request(*args, **kwargs)
    logging.debug(str(opts))

    if opts['scheme'] == 'https':
        connection = httplib.HTTPSConnection(opts['netloc'])
    else:
        connection = httplib.HTTPConnection(opts['netloc'])

    connection.request(opts['method'], opts['url'], opts['content'], opts['headers'])
    return connection.getresponse()

if __name__ == "__main__":
    import doctest
    doctest.testmod()
