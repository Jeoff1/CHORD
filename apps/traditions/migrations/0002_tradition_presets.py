from django.db import migrations

PRESETS = [
    ("alliance", "Alliance", "Christian and Missionary Alliance."),
    ("iglesia-ni-cristo", "Iglesia Ni Cristo", "Iglesia Ni Cristo (Church of Christ)."),
    ("roman-catholic", "Roman Catholic", "Roman Catholic Church."),
]


def load_presets(apps, schema_editor):
    Tradition = apps.get_model("traditions", "Tradition")
    for code, name, description in PRESETS:
        Tradition.objects.update_or_create(
            code=code, defaults={"name": name, "description": description}
        )


class Migration(migrations.Migration):
    dependencies = [("traditions", "0001_initial")]

    operations = [migrations.RunPython(load_presets, migrations.RunPython.noop)]
