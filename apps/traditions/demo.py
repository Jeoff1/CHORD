"""Demo church data per Tradition, loaded by ``manage.py seed_tradition``.

Every person, address and church here is fictional. Seeded accounts get an
unusable password unless the presenter supplies one at the command line.
Songs in metadata-only songbooks carry titles and metadata only.
Presets (Themes, Service Templates, Church Calendar, record types, songbooks)
come from data migrations; this module only links demo content to them.
"""

from datetime import date, datetime, time

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import Role, UserRole
from apps.members.models import Member
from apps.records.models import ChurchRecord, ChurchRecordType
from apps.worship.models import PlanSong, Song, Songbook, WorshipPlan

from .models import ServiceTemplate, Theme, Tradition
from .services import get_church_profile

DEMO_EMAIL_DOMAIN = "example.com"


def _user(username, first, last, roles):
    return {
        "username": username,
        "first_name": first,
        "last_name": last,
        "roles": roles,
    }


def _song(title, songbook, category, themes, key="", artist=""):
    return {
        "title": title,
        "songbook": songbook,
        "category": category,
        "themes": themes,
        "default_key": key,
        "artist": artist,
    }


DEMO_CHURCHES = {
    "roman-catholic": {
        "church_name": "St. Example Parish (Demo)",
        "location": "Demo Parish Church",
        "users": [
            _user("demo-rc-priest", "Paolo", "Demo", ["rc_parish_priest"]),
            _user("demo-rc-music", "Maria", "Sample", ["rc_music_director"]),
            _user("demo-rc-chorister", "Jose", "Placeholder", ["choir_member"]),
        ],
        "members": [("Ana", "Fictional"), ("Ben", "Testcase")],
        "songs": [
            _song(
                "Holy God, We Praise Thy Name", "catholic-hymnal", "hymn", ["praise"]
            ),
            _song(
                "O Come, O Come, Emmanuel",
                "catholic-hymnal",
                "hymn",
                ["advent", "hope"],
            ),
            _song(
                "Panis Angelicus", "catholic-hymnal", "hymn", ["eucharist", "communion"]
            ),
            _song("Hail, Holy Queen", "catholic-hymnal", "hymn", ["marian"]),
            _song("Silent Night", "general", "hymn", ["christmas", "peace"], key="C"),
            _song("Amazing Grace", "general", "hymn", ["grace"], key="G"),
        ],
        "plans": [
            {
                "title": "Second Sunday of Advent Mass (Demo)",
                "date": date(2026, 12, 6),
                "template": "mass",
                "theme": "advent",
                "songs": [
                    "O Come, O Come, Emmanuel",
                    "Amazing Grace",
                    "Panis Angelicus",
                    "Holy God, We Praise Thy Name",
                ],
            },
            {
                "title": "Christmas Day Mass (Demo)",
                "date": date(2026, 12, 25),
                "template": "mass",
                "theme": "christmas",
                "songs": ["Silent Night", "Hail, Holy Queen", "Panis Angelicus"],
            },
        ],
        "records": [
            ("Baptism", ("Ana", "Fictional"), "Fr. Demo Officiant", date(2026, 6, 14)),
            ("Marriage", ("Ben", "Testcase"), "Fr. Demo Officiant", date(2026, 9, 5)),
        ],
    },
    "alliance": {
        "church_name": "Example Alliance Church (Demo)",
        "location": "Demo Sanctuary",
        "users": [
            _user("demo-alliance-pastor", "Daniel", "Demo", ["alliance_senior_pastor"]),
            _user("demo-alliance-deacon", "Grace", "Sample", ["alliance_head_deacon"]),
            _user("demo-alliance-worship", "Samuel", "Placeholder", ["worship_leader"]),
            _user("demo-alliance-choir", "Ruth", "Fictional", ["choir_member"]),
        ],
        "members": [("Leah", "Testcase"), ("Caleb", "Example")],
        "songs": [
            _song("Amazing Grace", "general", "hymn", ["grace"], key="G"),
            _song(
                "Great Is Thy Faithfulness",
                "general",
                "hymn",
                ["faith", "thanksgiving"],
                key="D",
            ),
            _song(
                "It Is Well with My Soul", "general", "hymn", ["peace", "hope"], key="C"
            ),
            _song(
                "Jesus Shall Reign", "general", "hymn", ["missions", "praise"], key="D"
            ),
            _song("Holy, Holy, Holy", "general", "hymn", ["praise"], key="D"),
            _song(
                "Christ the Lord Is Risen Today",
                "general",
                "hymn",
                ["resurrection"],
                key="C",
            ),
        ],
        "plans": [
            {
                "title": "Thanksgiving Sunday Service (Demo)",
                "date": date(2026, 11, 22),
                "template": "worship-service",
                "theme": "thanksgiving",
                "songs": [
                    "Holy, Holy, Holy",
                    "Great Is Thy Faithfulness",
                    "Amazing Grace",
                    "It Is Well with My Soul",
                ],
            },
            {
                "title": "Missions Conference Sunday (Demo)",
                "date": date(2027, 2, 21),
                "template": "worship-service",
                "theme": "missions",
                "songs": ["Jesus Shall Reign", "Christ the Lord Is Risen Today"],
            },
        ],
        "records": [
            (
                "Baby Dedication",
                ("Caleb", "Example"),
                "Ptr. Demo Officiant",
                date(2026, 4, 12),
            ),
            ("Baptism", ("Leah", "Testcase"), "Ptr. Demo Officiant", date(2026, 8, 30)),
        ],
    },
    "iglesia-ni-cristo": {
        "church_name": "Example Local Congregation (Demo)",
        "location": "Demo House of Worship",
        "users": [
            _user("demo-inc-minister", "Ramon", "Demo", ["inc_minister"]),
            _user("demo-inc-deacon", "Liza", "Sample", ["inc_head_deacon"]),
            _user("demo-inc-choir", "Carlo", "Placeholder", ["choir_leader"]),
        ],
        "members": [("Nina", "Fictional"), ("Paolo", "Testcase")],
        # Placeholder titles only: the INC hymnal is metadata-only.
        "songs": [
            _song("Sample Hymn 1 (Demo)", "inc-hymnal", "hymn", ["praise"]),
            _song("Sample Hymn 2 (Demo)", "inc-hymnal", "hymn", ["unity"]),
            _song("Sample Hymn 3 (Demo)", "inc-hymnal", "hymn", ["thanksgiving"]),
            _song(
                "Sample Hymn 4 (Demo)", "inc-hymnal", "hymn", ["steadfastness", "faith"]
            ),
            _song("Sample Hymn 5 (Demo)", "inc-hymnal", "hymn", ["faithful-service"]),
        ],
        "plans": [
            {
                "title": "Year-End Thanksgiving Pagsamba (Demo)",
                "date": date(2026, 12, 27),
                "template": "pagsamba",
                "theme": "thanksgiving",
                "songs": [
                    "Sample Hymn 1 (Demo)",
                    "Sample Hymn 3 (Demo)",
                    "Sample Hymn 5 (Demo)",
                    "Sample Hymn 2 (Demo)",
                ],
            },
            {
                "title": "Midweek Pagsamba (Demo)",
                "date": date(2027, 1, 6),
                "template": "pagsamba",
                "theme": "unity",
                "songs": ["Sample Hymn 2 (Demo)", "Sample Hymn 4 (Demo)"],
            },
        ],
        "records": [
            ("Baptism", ("Nina", "Fictional"), "Bro. Demo Officiant", date(2026, 3, 8)),
            (
                "Marriage",
                ("Paolo", "Testcase"),
                "Bro. Demo Officiant",
                date(2026, 10, 17),
            ),
        ],
    },
}

SERVICE_TIME = time(9, 0)


@transaction.atomic
def seed_tradition(code, password=None):
    """Load the demo church for ``code`` and make it the active church.

    Existing demo rows are reused as they are, not updated. The first listed
    user is the author of the demo songs and plans.
    """
    demo = DEMO_CHURCHES[code]
    tradition = Tradition.objects.get(code=code)

    profile = get_church_profile()
    profile.tradition = tradition
    profile.name = demo["church_name"]
    profile.module_overrides = {}
    profile.save()

    users = [_seed_user(spec, password) for spec in demo["users"]]
    members = {
        (first, last): _seed_member(first, last) for first, last in demo["members"]
    }
    for user in users:
        members[(user.first_name, user.last_name)] = _seed_member(
            user.first_name, user.last_name, user=user
        )

    themes = Theme.objects.available_for(tradition)
    songs = {
        spec["title"]: _seed_song(spec, themes, created_by=users[0])
        for spec in demo["songs"]
    }
    for spec in demo["plans"]:
        _seed_plan(spec, tradition, themes, songs, demo["location"], users[0])
    for type_name, member_key, officiant, day in demo["records"]:
        record_type = ChurchRecordType.objects.get(tradition=tradition, name=type_name)
        ChurchRecord.objects.get_or_create(
            record_type=record_type,
            member=members[member_key],
            date=day,
            defaults={"officiant": officiant, "place": demo["location"]},
        )
    return profile


def _seed_user(spec, password):
    user, created = get_user_model().objects.get_or_create(
        username=spec["username"],
        defaults={
            "first_name": spec["first_name"],
            "last_name": spec["last_name"],
            "email": f"{spec['username']}@{DEMO_EMAIL_DOMAIN}",
        },
    )
    if password:
        user.set_password(password)
        user.save(update_fields=["password"])
    elif created:
        user.set_unusable_password()
        user.save(update_fields=["password"])
    for code in spec["roles"]:
        role = Role.objects.get(code=code)  # a missing role is a data error
        UserRole.objects.get_or_create(user=user, role=role)
    return user


def _seed_member(first, last, user=None):
    # Match on the demo email so a real member with the same name is never adopted.
    member, _ = Member.objects.get_or_create(
        email=f"{first}.{last}@{DEMO_EMAIL_DOMAIN}".lower(),
        defaults={
            "first_name": first,
            "last_name": last,
            "membership_status": Member.Status.MEMBER,
        },
    )
    if user and member.user_id is None:
        member.user = user
        member.save(update_fields=["user", "updated_at"])
    return member


def _seed_song(spec, themes, created_by):
    songbook = Songbook.objects.get(code=spec["songbook"])
    song, _ = Song.objects.get_or_create(
        title=spec["title"],
        songbook=songbook,
        defaults={
            "artist": spec["artist"],
            "category": spec["category"],
            "default_key": spec["default_key"],
            "created_by": created_by,
        },
    )
    song.themes.add(*themes.filter(code__in=spec["themes"]))
    return song


def _seed_plan(spec, tradition, themes, songs, location, created_by):
    template = ServiceTemplate.objects.get(tradition=tradition, code=spec["template"])
    plan, created = WorshipPlan.objects.get_or_create(
        title=spec["title"],
        defaults={
            "service_datetime": timezone.make_aware(
                datetime.combine(spec["date"], SERVICE_TIME)
            ),
            "location": location,
            "status": WorshipPlan.Status.PREPARING,
            "service_theme": themes.get(code=spec["theme"]),
            "service_template": template,
            "created_by": created_by,
        },
    )
    if not created:
        return plan
    slots = list(template.slots.all())
    # Songs fill slots in order; any extra songs share the last slot.
    for position, title in enumerate(spec["songs"], start=1):
        PlanSong.objects.create(
            plan=plan,
            song=songs[title],
            position=position,
            song_slot=slots[min(position, len(slots)) - 1],
            planned_key=songs[title].default_key,
        )
    return plan
