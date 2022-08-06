from django.urls import path

from .views import EpisodesFeed, upload

urlpatterns = [
    path('<str:podcast>/rss', EpisodesFeed(), name='feed'),
    path('<str:podcast>/upload', upload, name='upload'),
]
