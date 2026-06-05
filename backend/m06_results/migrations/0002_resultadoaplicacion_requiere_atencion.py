from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('m06_results', '0001_initial'),
    ]

    operations = [
        # Corregir CATEGORIA_CHOICES en ResultadoAplicacion
        migrations.AlterField(
            model_name='resultadoaplicacion',
            name='categoria',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('nulo',              'Nulo / despreciable'),
                    ('bajo',              'Bajo'),
                    ('medio',             'Medio'),
                    ('alto',              'Alto'),
                    ('muy_alto',          'Muy alto'),
                    ('requiere_atencion', 'Requiere atención clínica'),
                    ('sin_indicadores',   'Sin indicadores'),
                ],
            ),
        ),
        # Corregir CATEGORIA_CHOICES en ResultadoDominio
        migrations.AlterField(
            model_name='resultadodominio',
            name='categoria',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('nulo',              'Nulo / despreciable'),
                    ('bajo',              'Bajo'),
                    ('medio',             'Medio'),
                    ('alto',              'Alto'),
                    ('muy_alto',          'Muy alto'),
                    ('requiere_atencion', 'Requiere atención clínica'),
                    ('sin_indicadores',   'Sin indicadores'),
                ],
            ),
        ),
        # Agregar campo requiere_atencion
        migrations.AddField(
            model_name='resultadoaplicacion',
            name='requiere_atencion',
            field=models.BooleanField(
                blank=True,
                null=True,
                help_text='Solo Guía I. True = trabajador requiere evaluación clínica.',
            ),
        ),
    ]
