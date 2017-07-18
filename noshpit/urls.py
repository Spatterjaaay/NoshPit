from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^start$', views.start_a_pit, name='start'),
    url(r'^join$', views.join_a_pit, name='join'),
    url(r'^photos$', views.list_photos, name='photos'),
    url(r'^noshing$', views.start_noshing, name='start_noshing'),

]
