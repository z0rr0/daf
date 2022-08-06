from django import forms
from django.utils import timezone

from .models import Episode, Podcast


class EpisodeForm(forms.ModelForm):

    def __init__(self, *args, **kwargs) -> None:
        self.podcast: Podcast = kwargs.pop('podcast')
        super().__init__(*args, **kwargs)

    class Meta:
        model = Episode
        fields = ['title', 'image', 'public_image', 'author', 'description', 'audio', 'published']

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.podcast = self.podcast
        instance.published = instance.published or timezone.now()
        if commit:
            instance.save()
        return instance
