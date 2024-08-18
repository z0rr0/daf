#!/usr/bin/env python3
"""
Simple audio uploader for DAF.
Requirements:
    Markdown==3.4.1
    requests==2.28.1
"""
import io
import os
import sys
from dataclasses import dataclass

import argparse
import markdown
import requests


@dataclass(frozen=True)
class Params:
    base_url: str
    episode: io.BytesIO
    title: str
    image: io.BytesIO | None
    public_image: str
    author: str
    description: io.TextIOBase
    publish: bool
    slug: str
    name: str
    user: str
    password: str


class Uploader:

    def __init__(self, p: Params) -> None:
        self.params = p

    def upload(self) -> None:
        """Uploads the episode to DAF."""
        upload_url = f'{self.params.base_url}/podcast/{self.params.slug}/upload'
        description = markdown.markdown(self.params.description.read())

        data = {
            'title': self.params.title,
            'public_image': self.params.public_image,
            'author': self.params.author,
            'description': description,
            'publish': self.params.publish,
        }
        name = self.params.name or os.path.basename(self.params.episode.name)
        files = {'audio': (name, self.params.episode)}
        if self.params.image:
            files['image'] = (self.params.image.name, self.params.image)

        auth = (self.params.user, self.params.password) if self.params.user else None
        proxies = {
            'http': os.getenv('HTTP_PROXY'),
            'https': os.getenv('HTTPS_PROXY'),
        }

        print(f'start uploading {name} to {upload_url}')
        resp = requests.post(upload_url, data=data, files=files, auth=auth, proxies=proxies)

        json_statuses = {200, 400}
        response = resp.json() if resp.status_code in json_statuses else resp.text

        if resp.status_code != 200:
            print(f'status={resp.status_code}\n{response}', file=sys.stderr)
            sys.exit(1)

        print(response)

    def run(self):
        """Main method."""
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

    params = Params(
        base_url=namespace.base_url or os.getenv('DAF_URL') or 'http://127.0.0.1:8002',
        episode=namespace.episodes[0],
        title=namespace.title,
        image=namespace.image,
        public_image=namespace.public_image,
        author=namespace.author,
        description=namespace.description,
        publish=namespace.publish,
        slug=namespace.slug,
        name=namespace.name,
        user=namespace.user or os.getenv('DAF_USER'),
        password=namespace.password or os.getenv('DAF_PASSWORD'),
    )

    uploader = Uploader(params)
    uploader.run()
