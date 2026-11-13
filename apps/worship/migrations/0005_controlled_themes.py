from django.db import migrations, models

from apps.traditions.theme_matching import match_legacy_themes


def map_legacy_themes(apps, schema_editor):
    """Tag songs with matching Themes; keep only unmatched strings as legacy."""
    Song = apps.get_model("worship", "Song")
    Theme = apps.get_model("traditions", "Theme")
    ChurchProfile = apps.get_model("traditions", "ChurchProfile")
    # Only Themes the church can see: common plus the active Tradition's own.
    profile = ChurchProfile.objects.filter(pk=1).first()
    visible = models.Q(tradition__isnull=True)
    if profile is not None:
        visible |= models.Q(tradition_id=profile.tradition_id)
    themes = list(Theme.objects.filter(visible))
    for song in Song.objects.exclude(legacy_themes=[]):
        matched, unmatched = match_legacy_themes(song.legacy_themes, themes)
        song.themes.add(*matched)
        song.legacy_themes = unmatched
        song.save(update_fields=["legacy_themes"])


def restore_legacy_themes(apps, schema_editor):
    Song = apps.get_model("worship", "Song")
    for song in Song.objects.prefetch_related("themes"):
        tagged = [theme.name.lower() for theme in song.themes.all()]
        song.legacy_themes = tagged + list(song.legacy_themes)
        song.save(update_fields=["legacy_themes"])


class Migration(migrations.Migration):
    dependencies = [
        ("traditions", "0006_themes"),
        ("worship", "0004_songbooks"),
    ]

    operations = [
        migrations.RenameField(
            model_name="song", old_name="themes", new_name="legacy_themes"
        ),
        migrations.AlterField(
            model_name="song",
            name="legacy_themes",
            field=models.JSONField(
                blank=True,
                default=list,
                help_text="Free-string themes no controlled Theme matched; tag them by hand.",
            ),
        ),
        migrations.AddField(
            model_name="song",
            name="themes",
            field=models.ManyToManyField(
                blank=True, related_name="songs", to="traditions.theme"
            ),
        ),
        migrations.RunPython(map_legacy_themes, restore_legacy_themes),
    ]
