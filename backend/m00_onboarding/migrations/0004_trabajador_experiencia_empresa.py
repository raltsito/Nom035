from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('m00_onboarding', '0003_campos_guia_v'),
    ]

    operations = [
        migrations.AddField(
            model_name='trabajador',
            name='experiencia_empresa_anios',
            field=models.FloatField(blank=True, null=True, verbose_name='Experiencia en empresa actual (anos)'),
        ),
        migrations.AlterField(
            model_name='trabajador',
            name='experiencia_anios',
            field=models.FloatField(blank=True, null=True, verbose_name='Experiencia laboral (anos)'),
        ),
    ]
