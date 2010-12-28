
from django.conf.urls.defaults import *


urlpatterns = patterns('gamelogic.views',
    url(r'^data/$', 'xhr_key_data' , name='xhr_game_key'),
)
