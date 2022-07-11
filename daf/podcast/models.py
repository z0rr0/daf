from dataclasses import dataclass

from django.contrib import admin
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.syndication.views import add_domain
from django.db import models
from django.urls import reverse_lazy
from django.utils.html import format_html
from django.utils.timezone import get_default_timezone
from django.utils.translation import gettext_lazy as _


# ----------- additional ----------------
@dataclass(frozen=True)
class FeedRequest:
    """Class to generate absolute URLs for the feed's items."""
    domain: str
    secure: bool

    def url(self, url: str) -> str:
        return add_domain(self.domain, url, self.secure)


# ----------- abstract models -----------

class CreatedUpdatedModel(models.Model):
    created = models.DateTimeField(
        _('created'),
        auto_now_add=True, blank=True, db_index=True,
    )
    updated = models.DateTimeField(
        _('updated'),
        auto_now=True, blank=True, db_index=True,
    )

    class Meta:
        abstract = True


class PodcastBaseModel(CreatedUpdatedModel):
    title = models.CharField(_('title'), max_length=255, unique=True)
    image = models.ImageField(_('image'), upload_to='images', blank=True)
    author = models.CharField(_('author'), max_length=512, blank=True)
    description = models.TextField(_('description'), default='', blank=True)

    class Meta:
        abstract = True


# ----------- real models -----------


class Podcast(PodcastBaseModel):
    """Podcast objects. Every item results to a single RSS feed."""
    slug = models.SlugField(_('slug'), max_length=255, unique=True)
    link = models.URLField(_('link'), max_length=255, default='', blank=True)
    subtitle = models.CharField(
        _('subtitle'), max_length=512, default='', blank=True,
    )
    keywords = models.CharField(
        _('keywords'), max_length=512, default='', blank=True,
    )
    copyright = models.CharField(_('copyright'), max_length=512, blank=True)

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse_lazy('feed', args=[self.slug])

    @admin.display(description=_('feed'))
    def feed(self) -> str:
        url = self.get_absolute_url()
        return format_html(f'<a href={url}>xml</a>')

    def set_request(self, request) -> FeedRequest:
        current_site = get_current_site(request)
        self._request = FeedRequest(current_site.domain, request.is_secure())
        return self._request

    def abs_url(self, url: str) -> str:
        if r := getattr(self, '_request', None):
            return r.url(url)
        return ''

    @property
    def image_url(self) -> str:
        return self.abs_url(self.image.url)


def podcast_directory_path(episode: 'Episode', filename: str) -> str:
    return f'episodes/{episode.podcast.slug}/{filename}'


class Episode(PodcastBaseModel):
    """Podcasts' episodes."""
    podcast = models.ForeignKey(Podcast, on_delete=models.CASCADE)
    audio = models.FileField(_('audio'), upload_to=podcast_directory_path)
    published = models.DateTimeField(
        _('published'), blank=True, null=True, db_index=True,
    )

    def __str__(self) -> str:
        return f'{self.podcast.title} - {self.title}'

    def get_absolute_url(self) -> str:
        return self.audio.url

    @property
    def pub_date(self) -> str:
        if not self.published:
            return ''

        fmt = '%a, %d %b %Y %H:%M:%S %z'
        tz = get_default_timezone()
        value = self.published.replace(tzinfo=tz)
        return value.strftime(fmt)
