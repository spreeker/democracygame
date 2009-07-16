from django.conf.urls.defaults import *

from issue.models import Issue
from voting.views import vote

info = { 'queryset' : Issue.objects.all(), }
info_list = dict(info ,  paginate_by=3  )

urlpatterns = patterns('' ,
    (r'^$', 'django.views.generic.list_detail.object_list', info_list , ),
    (r'^page(?P<page>[0-9]+)/$', 'django.views.generic.list_detail.object_list', info_list , ),
    url(r'^(?P<object_id>\d+)/$', 'django.views.generic.list_detail.object_detail', info , name='issue_detail' ),
    url(r'^/vote/$' , vote , name='test_vote' ), 
)
