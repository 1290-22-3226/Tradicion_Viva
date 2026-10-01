from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("hermandades", "0014_administradororganizacion"),
    ]

    operations = [
        migrations.AddField(
            model_name="cuentadevoto",
            name="google_subject",
            field=models.CharField(
                blank=True,
                max_length=255,
                null=True,
                unique=True,
            ),
        ),
    ]