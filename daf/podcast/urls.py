from django.urls import path

from . import views
from .views import EpisodesFeed

urlpatterns = [
    path('', views.index, name='index'),
    path('<str:podcast>/rss', EpisodesFeed(), name='feed'),
]
