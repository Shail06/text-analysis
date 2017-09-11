from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^$', views.index, name = 'index'),
	url(r'training/$', views.training, name = 'training'),
	url(r'categorize/$', views.using, name = 'categorize'),
]
