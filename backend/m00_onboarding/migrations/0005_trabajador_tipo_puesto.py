from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('m00_onboarding', '0004_trabajador_experiencia_empresa'),
    ]

    operations = [
        migrations.AddField(
            model_name='trabajador',
            name='tipo_puesto',
            field=models.CharField(
                blank=True,
                choices=[
                    ('operativo',      'Operativo'),
                    ('administrativo', 'Administrativo'),
                    ('mandos_medios',  'Mandos medios / Supervisión'),
                    ('directivo',      'Directivo / Gerencial'),
                    ('otro',           'Otro'),
                ],
                max_length=20,
                verbose_name='Tipo de puesto',
            ),
        ),
    ]
