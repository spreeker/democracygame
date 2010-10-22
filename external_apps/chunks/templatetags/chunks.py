from django import template
from django.db import models
from django.core.cache import cache
from django.contrib.sites.models import Site

register = template.Library()

Chunk = models.get_model('chunks', 'Chunk')
CACHE_PREFIX = "chunk_"

def do_get_chunk(parser, token):
    # split_contents() knows not to split quoted strings.
    tokens = token.split_contents()
    if len(tokens) < 2 or len(tokens) > 3:
        raise template.TemplateSyntaxError, "%r tag should have either 2 or 3 arguments" % (tokens[0],)
    if len(tokens) == 2:
        tag_name, key = tokens
        cache_time = 0
    if len(tokens) == 3:
        tag_name, key, cache_time = tokens
    # Check to see if the key is properly double/single quoted
    if not (key[0] == key[-1] and key[0] in ('"', "'")):
        raise template.TemplateSyntaxError, "%r tag's argument should be in quotes" % tag_name
    # Send key (without quotes) and caching time
    return ChunkNode(key[1:-1], cache_time)
    
class ChunkNode(template.Node):
    def __init__(self, key, cache_time=0):
       self.key = key
       self.cache_time = int(cache_time)
       self.lang_code = template.Variable('LANGUAGE_CODE')
    
    def render(self, context):
        try:
            lang = self.lang_code.resolve(context)
        except template.VariableDoesNotExist:
            # no LANGUAGE_CODE variable found in context, just return ''
            return ''
        site = Site.objects.get_current().id  # Django caches get_current()
        cache_key = CACHE_PREFIX + self.key + lang + str(site)
        content = cache.get(cache_key)
        if content is None:
            try:
                chunk = Chunk.objects.get(key=self.key, lang_code=lang, site=site)
                content = chunk.content
            except Chunk.DoesNotExist:
                # cache missing models as empty chunk strings
                content = ''
            if self.cache_time > 0: 
                # don't even call cache if timeout is 0
                cache.set(cache_key, content, self.cache_time)
        return content

register.tag('chunk', do_get_chunk)
