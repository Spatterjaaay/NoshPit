from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^index.html$', views.home),
    url(r'^start$', views.start_a_pit, name='start'),
    url(r'^join$', views.join_a_pit, name='join'),
    url(r'^photos$', views.list_photos, name='photos'),
    url(r'^noshing$', views.start_noshing, name='start_noshing'),
    url(r'^yes$', views.yes, name='yes'),
    url(r'^winner_detail$', views.winner_detail, name='winner_detail'),
    url(r'^invite$', views.invite, name='invite'),
    url(r'^end_wait$', views.end_wait, name='end_wait'),
    url(r'^beg_wait$', views.beg_wait, name='beg_wait'),
    url(r'^no_winner$', views.no_winner, name='no_winner'),


]
