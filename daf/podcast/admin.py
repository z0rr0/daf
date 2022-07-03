from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Podcast, Episode


class PodcastAdmin(admin.ModelAdmin):
    list_display = ['title', 'link', 'image', 'description', 'created']
    search_fields = ('title', 'description')
    list_filter = ['created']


class EpisodeAdmin(admin.ModelAdmin):
    list_display = ['title', 'audio', 'published', 'created']
    search_fields = ('title', 'description')
    list_select_related = ['podcast']
    list_filter = ['created', 'podcast']


admin.site.register(Podcast, PodcastAdmin)
admin.site.register(Episode, EpisodeAdmin)
