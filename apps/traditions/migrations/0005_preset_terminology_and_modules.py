from django.db import migrations

ALL_MODULES = ["members", "ministries", "events", "giving", "worship"]

PRESETS = {
    "alliance": {
        "service": "Worship Service",
    },
    "iglesia-ni-cristo": {
        "service": "Pagsamba",
    },
    "roman-catholic": {
        "service": "Mass",
    },
}


def load_preset_settings(apps, schema_editor):
    Tradition = apps.get_model("traditions", "Tradition")
    for code, terminology in PRESETS.items():
        Tradition.objects.filter(code=code).update(
            terminology=terminology, default_modules=ALL_MODULES
        )


class Migration(migrations.Migration):
    dependencies = [("traditions", "0004_module_toggles_and_terminology")]

    operations = [migrations.RunPython(load_preset_settings, migrations.RunPython.noop)]
