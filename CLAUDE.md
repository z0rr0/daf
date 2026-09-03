# CLAUDE.md

This file provides guidance to coding agents when working with code in this repository.

## Project

**DAF (Django Audio Feed)** — a Django web app that turns uploaded audio files into custom iTunes-compatible RSS podcast feeds. Django 6.1, Python 3.14, dependencies managed with `uv` (`uv.lock`). There is no `requirements.txt`: the Docker build exports pinned runtime dependencies from `uv.lock` in a separate build stage.

## Commands

All commands run from the repo root. `manage.py` lives at `daf/manage.py`, so management commands are prefixed accordingly.

```sh
make test        # lint, then run the full test suite (this is `make all`)
make lint        # Ruff checks configured in pyproject.toml
make start       # run dev server at 127.0.0.1:8002 (backgrounded, PID in /tmp/.daf.pid)
make stop        # kill the dev server
make docker      # run tests, then build host-arch latest and version images
make docker-push # run tests, then build and push linux/amd64 and linux/arm64 images
```

Ruff targets Python 3.14 and enables `E`, `F`, `W`, `I`, `UP`, `B`, and `DJ` rules. Migrations and Django settings files are excluded. Run `uv run ruff check . --fix` to apply safe automatic fixes.

Run a single test (bypassing the lint gate in `make test`):

```sh
uv run daf/manage.py test podcast.tests.<TestClass>.<test_method>
```

Other management commands follow the same pattern, e.g. `uv run daf/manage.py migrate`, `uv run daf/manage.py createsuperuser`. Tests live in `daf/podcast/tests.py` and target the `podcast` app.

## Architecture

Single Django app (`daf/podcast/`) under a thin project config (`daf/daf/`). Two distinct surfaces:

**1. Feed generation (read path)** — `podcast/views.py`
- `EpisodesFeed` (subclass of Django's syndication `Feed`) renders a podcast's published episodes as RSS. It uses a custom feed type `ITunesFeed` (subclass of `Rss201rev2Feed`) that injects `itunes:` and `sy:` XML namespaces and elements for podcast-app compatibility.
- `CustomEpisodesFeed` exposes the *same* podcast under a UUID-based URL (the `CustomFeed` model), so a single podcast can have alternate, shareable feed links.
- Absolute URLs for audio/images are built per-request via `Podcast.set_request()` → `FeedRequest` (in `models.py`), since feeds need fully-qualified URLs.

**2. Episode upload (write path)** — the `upload` view
- `POST /podcast/<slug>/upload`, `@csrf_exempt` — it is meant to be protected by HTTP basic auth at the reverse-proxy layer, not in Django.
- Validation goes through `EpisodeForm` (`podcast/forms.py`); `clean_audio` rejects files whose extension isn't in the `MIME_TYPES` whitelist (defined in `settings.py`). The `publish` form flag sets the `published` timestamp, which is what makes an episode appear in the feed.

**Models** (`podcast/models.py`): `Podcast` 1—N `Episode` (cascade); `CustomFeed` N—1 `Podcast`. `Episode` and `Podcast` share `PodcastBaseModel` (title/image/author/description) and `CreatedUpdatedModel` (timestamps). `clean_files()` deletes the backing image/audio files from disk — be careful, it calls `os.remove` directly.

**URLs**: project `daf/urls.py` mounts the app at `/podcast/` and serves `MEDIA_URL` directly. App routes (`podcast/urls.py`): `<slug>/rss`, `<slug>/upload`, `custom/<uuid>`.

**Clients** (`clients/`): standalone CLI scripts (`youtube.py`, `simple.py`), *not* part of the Django app. They shell out (e.g. `youtube.py` runs `yt-dlp`) and POST to the `upload` endpoint over HTTP. They have their own informal dependency lists in their docstrings. Their Python dependencies (`markdown`, `requests`) live in the `clients` dependency group in `pyproject.toml`; it is installed locally by default via `tool.uv.default-groups` and excluded from the Docker image.

## Settings & secrets

- `daf/daf/settings.py` ends by importing `daf/daf/local_settings.py` (skipped when `test` is in `sys.argv`). Production secrets — `SECRET_KEY`, `DATABASES`, `DEBUG`, `ALLOWED_HOSTS` — belong in `local_settings.py`, **never** in `settings.py` (whose `SECRET_KEY`/`DEBUG=True` are insecure dev defaults).
- Database is SQLite (`daf/db.sqlite3`, committed). Deploy is Docker + uWSGI behind nginx (see `README.md`, `Dockerfile`, `uwsgi.ini`).

## CI

GitHub Actions (`.github/workflows/django.yml`) installs via `uv sync --all-extras --dev`, runs Ruff, then `make test` on Python 3.14. CodeQL analysis and Dependabot are also configured.
