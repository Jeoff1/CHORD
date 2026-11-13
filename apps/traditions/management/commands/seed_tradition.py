from django.core.management.base import BaseCommand, CommandError

from apps.traditions.demo import DEMO_CHURCHES, real_data_found, seed_tradition


class Command(BaseCommand):
    help = (
        "Load a fictional demo church for a Tradition and make it active. "
        "Safe to re-run: existing demo records are reused, not duplicated. "
        "Refuses a database that holds real church data unless --force is given."
    )

    def add_arguments(self, parser):
        parser.add_argument("tradition", help=", ".join(DEMO_CHURCHES))
        parser.add_argument(
            "--password",
            help="Set this password on every demo account; omit to leave them "
            "with unusable passwords. Never use a real password.",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Seed even though the database looks like a real church's. "
            "This overwrites the Church Profile.",
        )

    def handle(self, *args, tradition, password=None, force=False, **options):
        if tradition not in DEMO_CHURCHES:
            raise CommandError(
                f"Unknown tradition {tradition!r}; choose from {', '.join(DEMO_CHURCHES)}."
            )
        reasons = real_data_found()
        if reasons and not force:
            raise CommandError(
                "This database looks like a real church's: "
                + "; ".join(reasons)
                + ". Seeding would overwrite the Church Profile. "
                "Use a fresh database, or pass --force to seed anyway."
            )
        profile = seed_tradition(tradition, password=password)
        self.stdout.write(
            self.style.SUCCESS(f"Seeded {profile.name} ({profile.tradition}).")
        )
