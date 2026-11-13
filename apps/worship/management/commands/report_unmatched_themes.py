from django.core.management.base import BaseCommand

from apps.worship.models import Song


class Command(BaseCommand):
    help = "List songs whose legacy free-string themes matched no controlled Theme."

    def handle(self, *args, **options):
        songs = Song.objects.exclude(legacy_themes=[]).order_by("title")
        count = 0
        for song in songs:
            count += 1
            self.stdout.write(
                f"{song} ({song.public_id}): {', '.join(song.legacy_themes)}"
            )
        if count:
            self.stdout.write(f"{count} song(s) need manual theme tagging.")
        else:
            self.stdout.write(self.style.SUCCESS("No unmatched legacy themes."))
