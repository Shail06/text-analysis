from django.conf.urls import url

from . import views
from .views import ajax_view

urlpatterns = [
	url(r'^$', views.index, name = 'index'),
	url(r'^ajax/$', ajax_view.as_view()),
]
