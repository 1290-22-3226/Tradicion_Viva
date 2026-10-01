from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("hermandades", "0015_cuentadevoto_google_subject"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="cuentadevoto",
            name="google_subject",
        ),
    ]