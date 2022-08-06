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
import argparse
import io
import os
import subprocess
import sys
import tempfile
from datetime import datetime
from typing import Optional

import markdown
import requests


class YouTubeEpisodeHandler:
    URL = 'http://127.0.0.1:8002'

    def __init__(self, ns: argparse.Namespace) -> None:
        self.youtube_url: str = ns.url[0]

        self.title: str = ns.title
        self.image: Optional[io.BytesIO] = ns.image
        self.public_image: str = ns.public_image
        self.author: str = ns.author
        self.description: io.TextIOBase = ns.description
        self.publish: bool = ns.publish
        self.slug: str = ns.slug
        self.name: str = ns.name

        self.user: str = ns.user or os.getenv('DAF_USER')
        self.password: str = ns.password or os.getenv('DAF_PASSWORD')

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

    def prepare_audio(self) -> str:
        """Downloads the audio and returns its filename."""
        name = self._filename()
        print(f'temporary audio file: {name}')
        cmd = subprocess.run(
            ['yt-dlp', '-x', '--audio-format=mp3', '-o', name, self.youtube_url],
            capture_output=True,
            check=True,
        )
        print(cmd.stdout.decode())
        return name

    def prepare(self) -> str:
        """Does all preparation steps."""
        self.prepare_description()
        return self.prepare_audio()

    def upload(self, filename: str) -> None:
        """Uploads the episode to DAF."""
        upload_url = f'{self.URL}/podcast/{self.slug}/upload'
        data = {
            'title': self.title,
            'public_image': self.public_image,
            'author': self.author,
            'description': self.description,
            'publish': self.publish,
        }
        auth = (self.user, self.password) if self.user else None
        name = self.name or filename
        with open(filename, 'rb') as f:
            files = {'audio': (name, f)}
            if self.image:
                files['image'] = (self.image.name, self.image)
            resp = requests.post(upload_url, data=data, files=files, auth=auth)

        json_statuses = {200, 400}
        response = resp.json() if resp.status_code in json_statuses else resp.text

        print(response)
        if resp.status_code != 200:
            print(f'status={resp.status_code}\n{response}', file=sys.stderr)
            sys.exit(1)

        print(response)

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
    parser.add_argument('-t', dest='title', type=str, required=True, help='episode title')
    parser.add_argument('-i', dest='image', type=argparse.FileType('rb'), help='image file')
    parser.add_argument('-l', dest='public_image', type=str, help='public image url')
    parser.add_argument('-a', dest='author', type=str, help='episode author')
    parser.add_argument('-d', dest='description', type=argparse.FileType(), required=True, help='description file')
    parser.add_argument('-e', dest='publish', action='store_true', help='publish episode')

    parser.add_argument('-s', dest='slug', type=str, required=True, help='podcast slug')
    parser.add_argument('-n', dest='name', type=str, help='episode file name')
    parser.add_argument('-u', dest='user', type=str, help='basic auth user')
    parser.add_argument('-p', dest='password', type=str, help='basic auth password')

    parser.add_argument('url', nargs='+', type=str, help='youtube url')
    namespace, _ = parser.parse_known_args()

    uploader = YouTubeEpisodeHandler(namespace)
    uploader.run()
