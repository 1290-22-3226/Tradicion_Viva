from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("hermandades", "0013_videohermandad_video_alter_videohermandad_url"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AdministradorOrganizacion",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("activo", models.BooleanField(default=True)),
                ("creado_en", models.DateTimeField(auto_now_add=True)),
                ("actualizado_en", models.DateTimeField(auto_now=True)),
                (
                    "hermandad",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="administradores_asignados",
                        to="hermandades.hermandad",
                        verbose_name="hermandad o cofradía",
                    ),
                ),
                (
                    "usuario",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="asignacion_organizacion",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="usuario administrativo",
                    ),
                ),
            ],
            options={
                "verbose_name": "asignación de administrador",
                "verbose_name_plural": "asignaciones de administradores",
                "ordering": ["hermandad__nombre", "usuario__username"],
            },
        ),
    ]
