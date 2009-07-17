from piston.handler import BaseHandler, AnonymousBaseHandler
from piston.utils import rc, require_mime, require_extended

from blogserver.blog.models import Blogpost

class AnonymousBlogpostHandler(AnonymousBaseHandler):
    """
    Anonymous entrypoint for blogposts.
    """
    model = Blogpost
    fields = ('id', 'title', 'content', 'created_on')

    @classmethod
    def resource_uri(cls):
        return ('blogposts', [ 'format', ])

class BlogpostHandler(BaseHandler):
    """
    Authenticated entrypoint for blogposts.
    """
    model = Blogpost
    anonymous = AnonymousBlogpostHandler
    fields = ('title', 'content', ('author', ('username',)), 
              'created_on', 'content_length')

    @classmethod
    def content_length(cls, blogpost):
        return len(blogpost.content)

    @classmethod
    def resource_uri(cls):
        return ('blogposts', [ 'format', ])

    def read(self, request, title=None):
        """
        Returns a blogpost, if `title` is given,
        otherwise all the posts.
        
        Parameters:
         - `title`: The title of the post to retrieve.
        """
        base = Blogpost.objects
        
        if title:
            return base.get(title=title)
        else:
            return base.all()

    @require_extended
    def create(self, request):
        """
        Creates a new blogpost.
        """
        attrs = self.flatten_dict(request.POST)

        if self.exists(**attrs):
            return rc.DUPLICATE_ENTRY
        else:
            post = Blogpost(title=attrs['title'], 
                            content=attrs['content'],
                            author=request.user)
            post.save()
            
            return post
