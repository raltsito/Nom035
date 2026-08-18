"""Puebla Tenant.razon_social con las personas morales reales de LEAR,
tomadas de "Razon Social (Varias Plantas).docx" (documento enviado por el
cliente ago-2026). No todas las plantas son la misma persona moral: solo se
capturan aquí las que DIFIEREN de la razón social corporativa por defecto
(CONSORCIO INDUSTRIAL MEXICANO DE AUTOPARTES, S. DE R.L. DE C.V. —
`documents.views.RAZON_SOCIAL_CORPORATIVA`), que sigue siendo el fallback
para toda planta sin razón social propia. Mismo criterio de
0004_direcciones_plantas: solo escribe donde el campo está vacío, no pisa
capturas manuales previas.
"""

from django.db import migrations

_RAZON_SOCIAL = {
    'querétaro': 'GILL INDUSTRIES OF MEXICO, S. DE R.L. DE C.V.',
    'naucalpan': 'GILL INDUSTRIES OF MEXICO, S. DE R.L. DE C.V.',
    'reynosa': 'LEAR THERMAL COMFORT SYSTEMS MEXICO, S. DE R.L. DE C.V.',
    'agua prieta': 'LEAR THERMAL COMFORT SYSTEMS MEXICO, S. DE R.L. DE C.V.',
    'piedras negras i & ii': 'LEAR MEXICAN TRIM OPERATIONS, S. DE R.L. DE C.V.',
    'piedras negras iii': 'LEAR MEXICAN TRIM OPERATIONS, S. DE R.L. DE C.V.',
    'piedras negras iv': 'LEAR MEXICAN TRIM OPERATIONS, S. DE R.L. DE C.V.',
}


def poblar_razon_social(apps, schema_editor):
    Tenant = apps.get_model('tenants', 'Tenant')
    for tenant in Tenant.objects.filter(razon_social=''):
        valor = _RAZON_SOCIAL.get(tenant.nombre.strip().lower())
        if valor:
            tenant.razon_social = valor
            tenant.save(update_fields=['razon_social'])


def revertir(apps, schema_editor):
    Tenant = apps.get_model('tenants', 'Tenant')
    claves = set(_RAZON_SOCIAL)
    for tenant in Tenant.objects.all():
        if tenant.nombre.strip().lower() in claves:
            tenant.razon_social = ''
            tenant.save(update_fields=['razon_social'])


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0006_alter_tenant_razon_social'),
    ]

    operations = [
        migrations.RunPython(poblar_razon_social, revertir),
    ]
