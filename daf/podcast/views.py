from datetime import datetime
from typing import Any, Dict, Iterable, List

from django.conf import settings
from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Enclosure, Rss201rev2Feed

from .models import Episode, Podcast


class ITunesFeed(Rss201rev2Feed):
    def root_attributes(self):
        attrs = super().root_attributes()
        attrs['xmlns:itunes'] = 'http://www.itunes.com/dtds/podcast-1.0.dtd'
        return attrs

    def add_root_elements(self, handler):
        super().add_root_elements(handler)
        handler.addQuickElement('itunes:author', self.feed['author_name'])
        handler.addQuickElement('itunes:subtitle', self.feed['subtitle'])
        handler.addQuickElement('itunes:summary', self.feed['description'])
        handler.addQuickElement('itunes:image', self.feed['image'])
        handler.addQuickElement('itunes:keywords', self.feed['keywords'])
        handler.addQuickElement('itunes:explicit', 'no')

    def add_item_elements(self, handler, item):
        super().add_item_elements(handler, item)
        handler.addQuickElement('itunes:author', item['author_name'])
        handler.addQuickElement('itunes:summary', item['description'])
        handler.addQuickElement('itunes:image', item['image'])


class EpisodesFeed(Feed):
    feed_type = ITunesFeed
    language = settings.LANGUAGE_CODE

    def get_object(self, request, podcast: str, *args, **kwargs) -> Podcast:
        obj = Podcast.objects.get(slug=podcast)
        obj.set_request(request)
        return obj

    def title(self, obj: Podcast) -> str:
        return obj.title

    def subtitle(self, obj: Podcast) -> str:
        return obj.subtitle

    def description(self, obj: Podcast) -> str:
        return obj.description

    def link(self, obj: Podcast) -> str:
        return obj.get_absolute_url()

    def feed_url(self, obj: Podcast) -> str:
        return self.link(obj)

    def feed_guid(self, obj: Podcast) -> str:
        return obj.slug

    def author_name(self, obj: Podcast) -> str:
        return obj.author

    def feed_copyright(self, obj: Podcast) -> str:
        return obj.copyright

    def feed_extra_kwargs(self, obj: Podcast) -> Dict[str, Any]:
        return {
            'image': obj.image_url,
            'keywords': obj.keywords,
        }

    def items(self, obj: Podcast) -> Iterable[Episode]:
        items = obj.episode_set.filter(
            published__isnull=False,
        ).select_related('podcast').order_by('-published')
        for item in items:
            item.audio_url = obj.abs_url(item.audio.url)
            item.image_url = obj.abs_url(item.image.url) if item.image else ''
        return items

    def item_author_name(self, item: Episode) -> str:
        return item.author or item.podcast.author

    def item_title(self, item: Episode) -> str:
        return item.title

    def item_description(self, item: Episode) -> str:
        return item.description

    def item_link(self, item: Episode) -> str:
        return item.get_absolute_url()

    def item_enclosures(self, item: Episode) -> List[Enclosure]:
        return [Enclosure(
            url=getattr(item, 'audio_url', ''),
            length=str(item.audio.file.size),
            mime_type='audio/mp3'
        )]

    def item_pubdate(self, item: Episode) -> datetime:
        return item.published

    def item_guid(self, item: Episode) -> str:
        return str(item.pk)

    def item_extra_kwargs(self, item: Episode) -> Dict[str, Any]:
        return {'image': getattr(item, 'image_url', '')}
