from django.urls import path

from .views import EpisodesFeed

urlpatterns = [
    path('<str:podcast>/rss', EpisodesFeed(), name='feed'),
]
