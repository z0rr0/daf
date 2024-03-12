from django.contrib import admin

from .models import CustomFeed, Episode, Podcast


class PodcastAdmin(admin.ModelAdmin):
    list_display = ['title', 'link', 'feed', 'image', 'description', 'created']
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'description')
    list_filter = ['created']


class EpisodeAdmin(admin.ModelAdmin):
    list_display = ['title', 'audio', 'size', 'play', 'published', 'created']
    search_fields = ('title', 'description')
    list_select_related = ['podcast']
    list_filter = ['created', 'podcast', 'published']


class CustomFeedAdmin(admin.ModelAdmin):
    list_display = ['podcast', 'title', 'feed', 'created']
    search_fields = ('title',)
    list_select_related = ['podcast']
    list_filter = ['podcast', 'created']


admin.site.register(Podcast, PodcastAdmin)
admin.site.register(Episode, EpisodeAdmin)
admin.site.register(CustomFeed, CustomFeedAdmin)
