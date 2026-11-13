from django.db import migrations

RECORD_TYPES = {
    "roman-catholic": [
        "Baptism",
        "First Communion",
        "Confirmation",
        "Marriage",
        "Anointing of the Sick",
        "Funeral",
    ],
    "alliance": ["Baby Dedication", "Baptism", "Marriage", "Funeral"],
    "iglesia-ni-cristo": ["Child Dedication", "Baptism", "Marriage", "Funeral"],
}


def load_record_types(apps, schema_editor):
    Tradition = apps.get_model("traditions", "Tradition")
    ChurchRecordType = apps.get_model("records", "ChurchRecordType")
    for tradition in Tradition.objects.filter(code__in=RECORD_TYPES):
        for order, name in enumerate(RECORD_TYPES[tradition.code]):
            ChurchRecordType.objects.get_or_create(
                tradition=tradition, name=name, defaults={"sort_order": order}
            )
        # Enable the Church Records module by default for every preset.
        if "records" not in tradition.default_modules:
            tradition.default_modules = [*tradition.default_modules, "records"]
            tradition.save(update_fields=["default_modules"])


def unload(apps, schema_editor):
    Tradition = apps.get_model("traditions", "Tradition")
    for tradition in Tradition.objects.all():
        if "records" in tradition.default_modules:
            tradition.default_modules = [
                code for code in tradition.default_modules if code != "records"
            ]
            tradition.save(update_fields=["default_modules"])


class Migration(migrations.Migration):
    dependencies = [
        ("records", "0001_church_records"),
        ("traditions", "0008_church_calendar"),
    ]

    operations = [migrations.RunPython(load_record_types, unload)]
