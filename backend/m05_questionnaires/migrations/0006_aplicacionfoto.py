from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('m05_questionnaires', '0005_pregunta_opciones_respuestapregunta_valor_texto_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='AplicacionFoto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('actualizado_en', models.DateTimeField(auto_now=True)),
                ('foto', models.BinaryField(blank=True, null=True)),
                ('foto_mime', models.CharField(blank=True, max_length=80)),
                ('foto_tamanio', models.PositiveIntegerField(default=0)),
                ('estado', models.CharField(choices=[('capturada', 'Capturada'), ('omitida', 'Omitida')], max_length=20)),
                ('aplicacion', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='foto_guia', to='m05_questionnaires.aplicacion')),
                ('tenant', models.ForeignKey(db_index=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='tenants.tenant')),
            ],
            options={
                'verbose_name': 'Foto de aplicacion',
                'verbose_name_plural': 'Fotos de aplicaciones',
            },
        ),
    ]
