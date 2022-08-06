from django import forms
from django.utils import timezone

from .models import Episode, Podcast


class EpisodeForm(forms.ModelForm):
    publish = forms.BooleanField(label='publish', required=False)

    class Meta:
        model = Episode
        fields = ['title', 'image', 'public_image', 'author', 'description', 'audio']

    def __init__(self, *args, **kwargs) -> None:
        self.podcast: Podcast = kwargs.pop('podcast')
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.podcast = self.podcast

        if self.cleaned_data.get('publish'):
            instance.published = timezone.now()

        if commit:
            instance.save()
        return instance
