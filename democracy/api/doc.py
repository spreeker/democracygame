import logging

from django.core.urlresolvers import reverse
from piston.handler import typemapper
from piston.doc import generate_doc
from django.shortcuts import render_to_response
from django.template import RequestContext

from democracy.api.handlers import IssueList
from democracy.api.handlers import TagCloudHandler 

"""
Copied from piston.doc modified to apear in the way we want.
"""
def documentation_view(request):
    """
    Generic documentation view. Generates documentation
    from the handlers you've defined.
    """
    docs = [ ]
    
    issuedoc = generate_doc(IssueList)
    issuedoc.url = reverse("api_sort_order", args=["new"])
    docs.append(issuedoc)
    tagcloud = generate_doc(TagCloudHandler)
    tagcloud.url = reverse("api_tagcloud", args=["json"])
    docs.append(tagcloud)

    for handler, (model, anonymous) in typemapper.iteritems():
        docs.append(generate_doc(handler))

    def _compare( doc1 , doc2 ):
        return cmp(doc1.name, doc2.name)    
 
    docs.sort(_compare)

    return render_to_response('documentation.html', 
        { 'docs': docs }, RequestContext(request))
