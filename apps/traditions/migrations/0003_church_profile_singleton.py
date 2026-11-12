from django.db import migrations


def create_church_profile(apps, schema_editor):
    Tradition = apps.get_model("traditions", "Tradition")
    ChurchProfile = apps.get_model("traditions", "ChurchProfile")
    ChurchProfile.objects.get_or_create(
        pk=1, defaults={"tradition": Tradition.objects.get(code="alliance")}
    )


class Migration(migrations.Migration):
    dependencies = [("traditions", "0002_tradition_presets")]

    operations = [
        migrations.RunPython(create_church_profile, migrations.RunPython.noop)
    ]
