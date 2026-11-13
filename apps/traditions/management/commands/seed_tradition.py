from django.core.management.base import BaseCommand, CommandError

from apps.traditions.demo import DEMO_CHURCHES, seed_tradition


class Command(BaseCommand):
    help = (
        "Load a fictional demo church for a Tradition and make it active. "
        "Safe to re-run: existing demo records are reused, not duplicated."
    )

    def add_arguments(self, parser):
        parser.add_argument("tradition", help=", ".join(DEMO_CHURCHES))
        parser.add_argument(
            "--password",
            help="Set this password on every demo account; omit to leave them "
            "with unusable passwords. Never use a real password.",
        )

    def handle(self, *args, tradition, password=None, **options):
        if tradition not in DEMO_CHURCHES:
            raise CommandError(
                f"Unknown tradition {tradition!r}; choose from {', '.join(DEMO_CHURCHES)}."
            )
        profile = seed_tradition(tradition, password=password)
        self.stdout.write(
            self.style.SUCCESS(f"Seeded {profile.name} ({profile.tradition}).")
        )
