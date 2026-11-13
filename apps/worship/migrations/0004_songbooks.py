import django.db.models.deletion
from django.db import migrations, models

import apps.worship.models

# (code, name, metadata_only, tradition codes allowed to use it)
SONGBOOKS = [
    ("general", "General Library", False, ["alliance", "roman-catholic"]),
    ("catholic-hymnal", "Catholic Hymnal", True, ["roman-catholic"]),
    ("inc-hymnal", "INC Hymnal", True, ["iglesia-ni-cristo"]),
]


def load_songbooks(apps, schema_editor):
    Songbook = apps.get_model("worship", "Songbook")
    Tradition = apps.get_model("traditions", "Tradition")
    Song = apps.get_model("worship", "Song")
    for code, name, metadata_only, tradition_codes in SONGBOOKS:
        songbook, _ = Songbook.objects.update_or_create(
            code=code, defaults={"name": name, "metadata_only": metadata_only}
        )
        songbook.traditions.set(Tradition.objects.filter(code__in=tradition_codes))
    general = Songbook.objects.get(code="general")
    Song.objects.filter(songbook__isnull=True).update(songbook=general)


class Migration(migrations.Migration):
    dependencies = [
        ("traditions", "0005_preset_terminology_and_modules"),
        ("worship", "0003_rehearsal_songs_song_spotify_track_id_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Songbook",
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
                ("code", models.SlugField(unique=True)),
                ("name", models.CharField(max_length=150, unique=True)),
                (
                    "metadata_only",
                    models.BooleanField(
                        default=False,
                        help_text="Store titles and metadata only; refuse lyric and sheet resources.",
                    ),
                ),
                (
                    "traditions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Traditions whose setlists may use this songbook.",
                        related_name="songbooks",
                        to="traditions.tradition",
                    ),
                ),
            ],
            options={"ordering": ("name",)},
        ),
        migrations.AddField(
            model_name="song",
            name="metadata_only",
            field=models.BooleanField(
                default=False,
                help_text="Store metadata only; refuse lyric and sheet resources.",
            ),
        ),
        migrations.AddField(
            model_name="song",
            name="songbook",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="songs",
                to="worship.songbook",
            ),
        ),
        migrations.RunPython(load_songbooks, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="song",
            name="songbook",
            field=models.ForeignKey(
                default=apps.worship.models.default_songbook_id,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="songs",
                to="worship.songbook",
            ),
        ),
    ]
