#!/usr/bin/env python3
"""
YouTube audio uploader for DAF.

Manual mode:
1. Download audio with yt-dlp
    `yt-dlp -x --audio-format=mp3 -o audio.mp3 <URL>`
2. Go to DAF admin and create a new episode.

This script does the same automatically.

Requirements:
    Markdown==3.4.1
    yt-dlp==2022.7.18
    requests==2.28.1
"""
import io
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pprint import pprint
from typing import Optional

import argparse
import markdown
import requests


@dataclass(frozen=True)
class YouTubeParams:
    base_url: str
    youtube_url: str
    title: str
    image: Optional[io.BytesIO]
    public_image: str
    author: str
    description: io.TextIOBase
    publish: bool
    slug: str
    name: str
    password: str
    user: str


class YouTubeEpisodeHandler:

    def __init__(self, p: YouTubeParams) -> None:
        self.base_url: str = p.base_url or os.getenv('DAF_URL') or 'http://127.0.0.1:8002'
        self.youtube_url: str = p.youtube_url

        self.title: str = p.title
        self.image: Optional[io.BytesIO] = p.image
        self.public_image: str = p.public_image
        self.author: str = p.author
        self.description: io.TextIOBase = p.description
        self.publish: bool = p.publish
        self.slug: str = p.slug
        self.name: str = p.name

        self.user: str = p.user or os.getenv('DAF_USER')
        self.password: str = p.password or os.getenv('DAF_PASSWORD')

    @staticmethod
    def _filename() -> str:
        """Generates a temporary filename."""
        pid = os.getpid()
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        name = f'daf_youtube_{timestamp}_{pid}.mp3'
        return os.path.join(tempfile.gettempdir(), name)

    def prepare_description(self) -> None:
        """Converts the description from Markdown to HTML."""
        self.description = markdown.markdown(self.description.read())

    @staticmethod
    def get_env() -> dict[str, str]:
        """Returns environment variables for yt-dlp."""
        env = os.environ.copy()
        if http_proxy := os.getenv('HTTP_PROXY'):
            env['http_proxy'] = http_proxy

        if https_proxy := os.getenv('HTTPS_PROXY'):
            env['https_proxy'] = https_proxy

        return env

    def prepare_audio(self) -> str:
        """Downloads the audio and returns its filename."""
        name = self._filename()
        print(f'temporary audio file: {name}')

        subprocess.run(
            ['yt-dlp', '--progress', '--extract-audio', '--audio-format=mp3', '-o', name, self.youtube_url],
            capture_output=False,
            check=True,
            env=self.get_env()
        )
        return name

    @staticmethod
    def _size_mb(size: int) -> float:
        """Converts size in bytes to megabytes."""
        return size / 1024 / 1024

    def prepare(self) -> str:
        """Does all preparation steps."""
        self.prepare_description()
        filename = self.prepare_audio()

        stat_result = os.stat(filename)
        size_mb = self._size_mb(stat_result.st_size)
        print(f'audio file size: {stat_result.st_size} bytes ({size_mb:.2f} MB)')
        return filename

    def upload(self, filename: str) -> None:
        """Uploads the episode to DAF."""
        upload_url = f'{self.base_url}/podcast/{self.slug}/upload'
        data = {
            'title': self.title,
            'public_image': self.public_image,
            'author': self.author,
            'description': self.description,
            'publish': self.publish,
        }
        auth = (self.user, self.password) if self.user else None
        name = self.name or filename

        print(f'start uploading to {upload_url}')
        with open(filename, 'rb') as f:
            files = {'audio': (name, f)}
            if self.image:
                files['image'] = (self.image.name, self.image)
            resp = requests.post(upload_url, data=data, files=files, auth=auth)

        json_statuses = {200, 400}
        response = resp.json() if resp.status_code in json_statuses else resp.text

        if resp.status_code != 200:
            print(f'status={resp.status_code}\n{response}', file=sys.stderr)
            sys.exit(1)

        pprint(response, width=120)

    def run(self):
        """Main method."""
        filename = self.prepare()
        try:
            self.upload(filename)
        except Exception as e:
            print(f'upload error\n{e}', file=sys.stderr)
            sys.exit(2)
        finally:
            # delete temporary file
            os.path.exists(filename) and os.remove(filename)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='YouTube audio DAF uploader')
    parser.add_argument('-b', dest='base_url', type=str, help='DAF base URL (env DAF_URL)')
    parser.add_argument('-t', dest='title', type=str, required=True, help='episode title')
    parser.add_argument('-i', dest='image', type=argparse.FileType('rb'), help='image file')
    parser.add_argument('-l', dest='public_image', type=str, help='public image url')
    parser.add_argument('-a', dest='author', type=str, help='episode author')
    parser.add_argument('-d', dest='description', type=argparse.FileType(), required=True, help='description file')
    parser.add_argument('-e', dest='publish', action='store_true', help='publish episode')

    parser.add_argument('-s', dest='slug', type=str, default='youtube', help='podcast slug (default "youtube")')
    parser.add_argument('-n', dest='name', type=str, help='episode file name')
    parser.add_argument('-u', dest='user', type=str, help='basic auth user (default env DAF_USER)')
    parser.add_argument('-p', dest='password', type=str, help='basic auth password (default env DAF_PASSWORD)')

    parser.add_argument('url', nargs='+', type=str, help='youtube url')
    namespace, _ = parser.parse_known_args()

    params = YouTubeParams(
        base_url=namespace.base_url,
        youtube_url=namespace.url[0],
        title=namespace.title,
        image=namespace.image,
        public_image=namespace.public_image,
        author=namespace.author,
        description=namespace.description,
        publish=namespace.publish,
        slug=namespace.slug,
        name=namespace.name,
        user=namespace.user,
        password=namespace.password,
    )

    uploader = YouTubeEpisodeHandler(params)
    uploader.run()
