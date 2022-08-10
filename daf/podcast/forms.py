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

    def clean_audio(self):
        audio = self.cleaned_data.get('audio')
        if audio:
            mime_type = Episode.get_mime_type(audio.name)
            if not mime_type:
                raise forms.ValidationError('invalid audio file type', code='invalid_type')
        return audio

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.podcast = self.podcast

        if self.cleaned_data.get('publish'):
            instance.published = timezone.now()

        if commit:
            instance.save()
        return instance
