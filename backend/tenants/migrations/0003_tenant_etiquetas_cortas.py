from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0002_tenant_direccion_tenant_logo_url_tenant_sitio_web_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tenant',
            name='etiquetas_cortas',
            field=models.BooleanField(default=False, verbose_name='Usar etiquetas cortas de tipo personal'),
        ),
    ]
