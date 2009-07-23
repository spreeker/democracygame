import logging

from piston.handler import typemapper
from piston.doc import generate_doc
from django.shortcuts import render_to_response
from django.template import RequestContext

"""
Copied from piston.doc modified to apear in the way we want.
"""
def documentation_view(request):
    """
    Generic documentation view. Generates documentation
    from the handlers you've defined.
    """
    docs = [ ]

    for handler, (model, anonymous) in typemapper.iteritems():
        docs.append(generate_doc(handler))

    def _compare( doc1 , doc2 ):
        return cmp(doc1.name , doc2.name)    
 
    docs.sort(_compare)

    return render_to_response('documentation.html', 
        { 'docs': docs }, RequestContext(request))
