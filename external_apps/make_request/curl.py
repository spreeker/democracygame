from make_request import prepare_request
from memoize import cached_property
import cStringIO as StringIO
import pycurl
import httplib

CONNECTTIMEOUT = 5
TIMEOUT = 30

class FakeSock(object):
    def __init__(self, fp):
        self.fp = fp

    def makefile(self, a, b):
        return self.fp

class CurlResponse(httplib.HTTPResponse):
    #FIXME redirects/follow_location probably breaks this
    def __init__(self, handle, *args, **kwargs):
        self.handle = handle
        self.handle.fp.seek(0)
        httplib.HTTPResponse.__init__(self, FakeSock(handle.fp), *args, **kwargs)
        self.begin()

    def read(self, *args, **kwargs):
        return self.fp.read(*args, **kwargs)

def prepare_curl_handle(opts):
    curl_opts = opts.pop('curl', {})
    url = opts['scheme'] + '://' + opts['netloc'] + opts['url']
    c = pycurl.Curl()
    c.setopt(pycurl.CONNECTTIMEOUT, curl_opts.pop(pycurl.CONNECTTIMEOUT, CONNECTTIMEOUT))
    c.setopt(pycurl.TIMEOUT, curl_opts.pop(pycurl.TIMEOUT, TIMEOUT))
    [c.setopt(opt, value) for opt, value in curl_opts.iteritems()]
    c.fp = StringIO.StringIO()
    c.setopt(pycurl.WRITEFUNCTION, c.fp.write)
    c.setopt(pycurl.URL, url)
    c.setopt(pycurl.CUSTOMREQUEST, opts['method'])
    c.setopt(pycurl.HEADER, True)
    if opts['content']:
        c.setopt(pycurl.POSTFIELDS, opts['content'])
    #FIXME headers need to be flattened. add support for tuples
    #c.setopt(pycurl.headers, opts['headers'])
    return c

def make_request(*args, **kwargs):
    """
    >>> ECHO_URL = 'http://json-service.appspot.com/echo'

    POST request with array value using parameters.
    >>> response = make_request(ECHO_URL, 'POST', {'a':1, 'b': [2,3]})
    >>> response.status
    200
    >>> import json
    >>> j = json.loads(response.read())
    >>> j['method']
    u'POST'
    >>> j['path']
    u'/echo'
    >>> j['query_params']
    {}
    >>> j['post_params']
    {u'a': u'1', u'b': [u'2', u'3']}

    """

    c = prepare_curl_handle(prepare_request(*args, **kwargs))
    c.perform()
    return CurlResponse(c)

def multi_requests(*requests):
    """
    >>> SLEEP_URL = 'http://json-service.appspot.com/sleep'

    The order of responses matches the order of requests.
    >>> r1 = {'url': SLEEP_URL, 'content': {'seconds': 3}}
    >>> r2 = {'url': SLEEP_URL, 'content': {'seconds': 1}}
    >>> responses = multi_requests(r1, r2)
    >>> responses[0].read()
    'Slept for 3'
    >>> responses[1].read()
    'Slept for 1'

    The order of callbacks matches the order of responses from the servers.
    >>> responses_bytime = []
    >>> c = lambda r: responses_bytime.append(r)
    >>> r1 = {'url': SLEEP_URL, 'content': {'seconds': 3}, 'callback': c}
    >>> r2 = {'url': SLEEP_URL, 'content': {'seconds': 1}, 'callback': c}
    >>> responses_original = multi_requests(r1, r2)
    >>> responses_bytime[0].read()
    'Slept for 1'
    >>> responses_bytime[1].read()
    'Slept for 3'
    >>> responses_original[0] is responses_bytime[1]
    True
    >>> responses_original[1] is responses_bytime[0]
    True

    """
    handles = []
    responses = []
    handles_len = 0
    for r in requests:
        callback = r.pop('callback', None)
        c = prepare_curl_handle(prepare_request(**r))
        c.callback = callback
        c.index = handles_len
        handles_len += 1
        handles.append(c)
        responses.append(None) # append a None for each corresponding handle

    multi = pycurl.CurlMulti()
    map(multi.add_handle, handles)
    num_processed = 0
    while num_processed < handles_len:
        # run the curl state machine until we have something to do
        while 1:
            ret, num_handles = multi.perform()
            if ret != pycurl.E_CALL_MULTI_PERFORM:
                break
        # check which handles have terminated
        while 1:
            num_q, ok_list, err_list = multi.info_read()
            for c in ok_list:
                response = CurlResponse(c)
                responses[c.index] = response
                if c.callback:
                    c.callback(response)
                multi.remove_handle(c)
            for c, errno, errmsg in err_list:
                response = CurlResponse(c, errno, errmsg)
                responses[c.index] = response
                multi.remove_handle(c)
            num_processed = num_processed + len(ok_list) + len(err_list)
            if num_q == 0:
                break
        # Currently no more I/O is pending, could do something in the meantime
        # We just call select() to sleep until some more data is available.
        multi.select(1.0)

    return responses
