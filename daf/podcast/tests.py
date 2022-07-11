from datetime import timedelta
from django.utils import timezone

from django.core.files.base import ContentFile
from django.test import TestCase

from .models import Episode, Podcast


class FeedTestCase(TestCase):
    URL = '/podcast/{}/rss'

    def setUp(self) -> None:
        super().setUp()

        self.podcasts = [
            Podcast.objects.create(
                author=f'Author{i}',
                description=f'Description{i}',
                title=f'Podcast{i}',
                keywords=f'Keywords{i}',
                link=f'https://github.com/z0rr0/daf/{i}',
                subtitle=f'Subtitle{i}',
                slug=f'podcast{i}',
                copyright=f'Copyright{i}',
                image=ContentFile(b'file', name=f'image{1}.png'),
            )
            for i in range(2)
        ]
        now = timezone.now()
        self.episodes = {
            p.id: [
                Episode.objects.create(
                    podcast=p,
                    author=f'Episode Author{j}',
                    description=f'Episode Description{j}',
                    title=f'Episode Podcast {p.id} {j}',
                    published=now - timedelta(days=1) if j % 2 else None,
                    image=ContentFile(b'file', name=f'episode image{j}.png'),
                    audio=ContentFile(b'audio', name=f'audio{j}.mp3'),
                )
                for j in range(10)
            ]
            for p in self.podcasts
        }

    def test_not_found(self):
        resp = self.client.get(self.URL.format('not-found'))
        self.assertEqual(resp.status_code, 404)

    def test_feed(self):
        podcast = self.podcasts[0]
        resp = self.client.get(self.URL.format(podcast.slug))
        self.assertEqual(resp.status_code, 200)

        episodes = [
            episode
            for episode in self.episodes[podcast.id]
            if episode.published is not None
        ]
        episodes.sort(key=lambda e: e.published, reverse=True)
        self.assertEqual(len(episodes), 5)

        pub_date = episodes[0].pub_date
        expected = (f"""<?xml version="1.0" encoding="utf-8"?>
            <rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
            <channel xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
            <title>{podcast.title}</title>
            <link>http://testserver/podcast/{podcast.slug}/rss</link>
            <description>{podcast.description}</description>
            <atom:link href="http://testserver/podcast/podcast0/rss"
            \trel="self"/>
            <language>en-us</language>
            <copyright>{podcast.copyright}</copyright>
            <lastBuildDate>{pub_date}</lastBuildDate>
            <itunes:author>{podcast.author}</itunes:author>
            <itunes:subtitle>{podcast.subtitle}</itunes:subtitle>
            <itunes:summary>{podcast.description}</itunes:summary>
            <itunes:image>http://testserver{podcast.image.url}</itunes:image>
            <itunes:keywords>{podcast.keywords}</itunes:keywords>
            <itunes:explicit>no</itunes:explicit>""")

        items = [
            f"""<item><title>{episode.title}</title>
            <link>http://testserver{episode.audio.url}</link>
            <description>{episode.description}</description>
            <dc:creator xmlns:dc="http://purl.org/dc/elements/1.1/">
            {episode.author}</dc:creator>
            <pubDate>{episode.pub_date}</pubDate>
            <guid>{episode.id}</guid>
            <enclosure length="5" type="audio/mp3"
            \turl="http://testserver{episode.audio.url}"/>
            <itunes:author>{episode.author}</itunes:author>
            <itunes:summary>{episode.description}</itunes:summary>
            <itunes:image>http://testserver{episode.image.url}</itunes:image>
            </item>"""
            for episode in episodes
        ]
        expected += ''.join(items)
        expected += '</channel></rss>'

        expected = expected.replace('\n', '').replace('    ', '')
        expected = expected.replace('\t', ' ')
        result = resp.content.decode('utf-8').replace('\n', '')

        self.assertEqual(result, expected)
