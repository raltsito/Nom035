from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('m00_onboarding', '0006_trabajador_tipo_puesto_libre'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trabajador',
            name='tipo_jornada',
            field=models.CharField(
                blank=True,
                choices=[
                    ('diurno',          'Diurno'),
                    ('mixto',           'Mixto'),
                    ('nocturno',        'Nocturno'),
                    ('tiempo_completo', 'Tiempo completo'),
                ],
                max_length=15,
                verbose_name='Tipo de jornada',
            ),
        ),
    ]
