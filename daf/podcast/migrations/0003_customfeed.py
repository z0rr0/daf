# Generated by Django 5.0.3 on 2024-03-12 11:29

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("podcast", "0002_episode_public_image_podcast_public_image"),
    ]

    operations = [
        migrations.CreateModel(
            name="CustomFeed",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True, db_index=True, verbose_name="created"
                    ),
                ),
                (
                    "updated",
                    models.DateTimeField(
                        auto_now=True, db_index=True, verbose_name="updated"
                    ),
                ),
                (
                    "ref",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        unique=True,
                        verbose_name="reference",
                    ),
                ),
                ("title", models.CharField(max_length=255, verbose_name="title")),
                (
                    "podcast",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="podcast.podcast",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
