#!/usr/bin/env python3
"""
Simple audio uploader for DAF.
Requirements:
    Markdown==3.4.1
    requests==2.28.1
"""
import argparse
import io
import os
import sys
from typing import Optional

import markdown
import requests


class Uploader:

    def __init__(self, ns: argparse.Namespace) -> None:
        self.base_url: str = ns.base_url or os.getenv('DAF_URL') or 'http://127.0.0.1:8002'
        self.episode: io.BytesIO = ns.episodes[0]

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

    def prepare_description(self) -> None:
        """Converts the description from Markdown to HTML."""
        self.description = markdown.markdown(self.description.read())

    def upload(self) -> None:
        """Uploads the episode to DAF."""
        upload_url = f'{self.base_url}/podcast/{self.slug}/upload'
        data = {
            'title': self.title,
            'public_image': self.public_image,
            'author': self.author,
            'description': self.description,
            'publish': self.publish,
        }
        name = self.name or os.path.basename(self.episode.name)
        files = {'audio': (name, self.episode)}
        if self.image:
            files['image'] = (self.image.name, self.image)
        auth = (self.user, self.password) if self.user else None

        print(f'start uploading {name} to {upload_url}')
        resp = requests.post(upload_url, data=data, files=files, auth=auth)

        json_statuses = {200, 400}
        response = resp.json() if resp.status_code in json_statuses else resp.text

        if resp.status_code != 200:
            print(f'status={resp.status_code}\n{response}', file=sys.stderr)
            sys.exit(1)

        print(response)

    def run(self):
        """Main method."""
        self.prepare_description()
        self.upload()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='simple DAF uploader')
    parser.add_argument('-b', dest='base_url', type=str, help='DAF base URL (default env DAF_URL)')
    parser.add_argument('-t', dest='title', type=str, required=True, help='episode title')
    parser.add_argument('-i', dest='image', type=argparse.FileType('rb'), help='image file')
    parser.add_argument('-l', dest='public_image', type=str, help='public image url')
    parser.add_argument('-a', dest='author', type=str, required=True, help='episode author')
    parser.add_argument('-d', dest='description', type=argparse.FileType(), required=True, help='description file')
    parser.add_argument('-e', dest='publish', action='store_true', help='publish episode')

    parser.add_argument('-s', dest='slug', type=str, default='diary', help='podcast slug (default "diary")')
    parser.add_argument('-n', dest='name', type=str, help='episode file name')
    parser.add_argument('-u', dest='user', type=str, help='basic auth user (default env DAF_USER)')
    parser.add_argument('-p', dest='password', type=str, help='basic auth password (default env DAF_PASSWORD)')

    parser.add_argument('episodes', nargs='+', type=argparse.FileType('rb'), help='episodes audio files')
    namespace, _ = parser.parse_known_args()

    uploader = Uploader(namespace)
    uploader.run()
