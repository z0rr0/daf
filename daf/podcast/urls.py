from django.urls import path

from .views import CustomEpisodesFeed, EpisodesFeed, upload

urlpatterns = [
    path('<str:podcast>/rss', EpisodesFeed(), name='feed'),
    path('<str:podcast>/upload', upload, name='upload'),
    path('custom/<uuid:ref>', CustomEpisodesFeed(), name='custom_feed'),
]
