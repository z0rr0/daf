from django.db import models
from django.utils.translation import gettext_lazy as _


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


# ----------- real models -----------

class Podcast(CreatedUpdatedModel):
    title = models.CharField(_('title'), max_length=255, unique=True)
    link = models.URLField(_('link'), max_length=255, default='', blank=True)
    image = models.ImageField(_('image'), upload_to='images', blank=True)
    author = models.CharField(_('author'), max_length=512, blank=True)
    description = models.TextField(_('description'), default='', blank=True)
    subtitle = models.CharField(
        _('subtitle'), max_length=512, default='', blank=True,
    )
    keywords = models.CharField(
        _('keywords'), max_length=512, default='', blank=True,
    )

    def __str__(self) -> str:
        return self.title


def podcast_directory_path(episode: 'Episode', filename: str) -> str:
    return f'episodes/podcast_{episode.podcast.id}/{filename}'


class Episode(CreatedUpdatedModel):
    podcast = models.ForeignKey(Podcast, on_delete=models.CASCADE)
    title = models.CharField(_('title'), max_length=255, db_index=True)
    audio = models.FileField(
        _('audio'), upload_to=podcast_directory_path, blank=True,
    )
    description = models.TextField(
        _('description'), default='', blank=True,
    )
    published = models.DateTimeField(
        _('published'), blank=True, null=True, db_index=True,
    )

    def __str__(self) -> str:
        return f'{self.podcast.title} - {self.title}'
