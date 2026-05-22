from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('m00_onboarding', '0005_trabajador_tipo_puesto'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trabajador',
            name='tipo_puesto',
            field=models.CharField(blank=True, max_length=100, verbose_name='Tipo de puesto'),
        ),
    ]
