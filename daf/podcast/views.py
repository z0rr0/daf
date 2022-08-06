from datetime import datetime
from typing import Any, Dict, Iterable, List

from django.conf import settings
from django.contrib.syndication.views import Feed
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.utils.feedgenerator import Enclosure, Rss201rev2Feed
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .forms import EpisodeForm
from .models import Episode, Podcast


class ITunesFeed(Rss201rev2Feed):
    """Extension to the RSS v2 feed class to add iTunes specific elements."""

    def rss_attributes(self):
        attrs = super().rss_attributes()
        attrs.update({
            'xmlns:itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd'
        })
        return attrs

    def _image(self, handler):
        handler.startElement('image', {})
        handler.addQuickElement('title', self.feed['title'])
        handler.addQuickElement('url', self.feed['image'])
        handler.addQuickElement('link', self.feed['link'])
        handler.endElement('image')

    def add_root_elements(self, handler):
        super().add_root_elements(handler)

        handler.addQuickElement('sy:updatePeriod', 'hourly')
        handler.addQuickElement('sy:updateFrequency', '1')

        handler.addQuickElement('itunes:author', self.feed['author_name'])
        handler.addQuickElement('itunes:subtitle', self.feed['subtitle'])
        handler.addQuickElement('itunes:summary', self.feed['description'])
        handler.addQuickElement('itunes:keywords', self.feed['keywords'])
        handler.addQuickElement('itunes:explicit', 'no')
        handler.addQuickElement(
            'itunes:image',
            attrs={'href': self.feed['image']},
        )
        self._image(handler)

    def add_item_elements(self, handler, item):
        super().add_item_elements(handler, item)
        handler.addQuickElement('itunes:author', item['author_name'])
        handler.addQuickElement('itunes:summary', item['description'])
        handler.addQuickElement('itunes:image', attrs={'href': item['image']})


class EpisodesFeed(Feed):
    """Main feed generator class."""
    feed_type = ITunesFeed
    language = settings.LANGUAGE_CODE
    ttl = settings.PODCAST_TTL

    def get_object(self, request, *args, **kwargs) -> Podcast:
        obj = Podcast.objects.get(slug=kwargs.get('podcast'))
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
            item.image_url = obj.abs_url(item.image.url) if item.image else item.public_image
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


@require_POST
@csrf_exempt  # method is to be protected by basic auth
def upload(request, podcast: str) -> HttpResponse:
    """Upload a new episode to a podcast."""
    podcast = get_object_or_404(Podcast, slug=podcast)
    form = EpisodeForm(request.POST, request.FILES, podcast=podcast)
    if not form.is_valid():
        errors = form.errors.as_json()
        return HttpResponseBadRequest(f'oops, errors: {errors}')

    episode = form.save()
    return HttpResponse(f'ok, episode "{episode.title}" uploaded, id={episode.id}')
