"""Puebla Tenant.direccion con los domicilios reales de las 16 plantas
conocidas, tomados de `_DIR` en `generar_informe.py` (script validado con
el cliente). Formato: 'Calle y No | Colonia | Municipio | Estado' — el
render del informe (documents/docx_builder.py::_add_datos_centro_trabajo)
divide por ' | ' para mostrar las 4 líneas etiquetadas del documento de
referencia. Solo actualiza tenants cuyo nombre coincide (case-insensitive)
y cuya dirección esté vacía — no pisa datos ya capturados manualmente.
"""

from django.db import migrations

_DIRECCIONES = {
    'piedras negras i & ii': (
        'Blvd. República No. 130',
        'Desarrollo Industrial Río Grande, C.P. 26080',
        'Piedras Negras',
        'Coahuila',
    ),
    'piedras negras iii': (
        'Blvd. República #102',
        'Desarrollo Industrial Río Grande',
        'Piedras Negras',
        'Coahuila',
    ),
    'piedras negras iv': (
        'Blvd. República',
        'Desarrollo Industrial Río Grande, C.P. 26080',
        'Piedras Negras',
        'Coahuila',
    ),
    'san luis': (
        'Circuito Exportación No. 311',
        'Zona Industrial',
        'San Luis Potosí',
        'S.L.P., C.P. 78395',
    ),
    'puebla': (
        'Calle Acacias Nave 13',
        'Parque Industrial Finsa, Cuautlancingo',
        'Puebla',
        'Puebla, C.P. 72710',
    ),
    'hermosillo': (
        'Calle de Los Olivos #1',
        'Col. Parque Industrial',
        'Hermosillo',
        'Sonora, C.P. 83299',
    ),
    'planta 726 ramos': (
        'Libramiento Oscar Flores Tapia 1755',
        'Parque Industrial Amistad II',
        'Ramos Arizpe',
        'Coahuila, C.P. 25900',
    ),
    'naucalpan': (
        'Calle 8 No. 2-A',
        'Alce Blanco',
        'Naucalpan',
        'Estado de México, C.P. 53370',
    ),
    'reynosa': (
        'Ave. Progreso Edificio 3 Suite #310, Ave. El Puente y Canal Pluvial',
        '',
        'Reynosa',
        'Tamaulipas, C.P. 88783',
    ),
    'silao': (
        'Av. Paraíso 449',
        'Parque Industrial Colinas',
        'Silao de la Victoria',
        'Guanajuato, C.P. 36113',
    ),
    'toluca': (
        'Manzana 015',
        'Delegación Santa María Totoltepec',
        'Santa María Totoltepec',
        'Estado de México, C.P. 50200',
    ),
    'saltillo': (
        'Blvd. Jesús Valdez Sanchez 4223',
        'La Aurora',
        'Saltillo',
        'Coahuila, C.P. 25298',
    ),
    'zapotitlan': (
        'Av. Tláhuac 6732',
        'Santiago Zapotitlan, C.P. 13300',
        'Tlahuac',
        'CDMX',
    ),
    'arteaga': (
        'Blvd. Minero 507',
        'Parque Industrial Server',
        'Arteaga',
        'Coahuila, C.P. 25350',
    ),
    'querétaro': (
        'Av. Benito Juárez 118',
        'Parque Industrial Querétaro',
        'Queretaro',
        'Querétaro, C.P. 76215',
    ),
    'huamantla': (
        'Calle Huamantla Lote 17',
        'Ciudad Industrial Xicohtencatl II',
        'Huamantla',
        'Tlaxcala',
    ),
}


def poblar_direcciones(apps, schema_editor):
    Tenant = apps.get_model('tenants', 'Tenant')
    for tenant in Tenant.objects.filter(direccion=''):
        partes = _DIRECCIONES.get(tenant.nombre.strip().lower())
        if partes:
            tenant.direccion = ' | '.join(partes)
            tenant.save(update_fields=['direccion'])


def revertir(apps, schema_editor):
    Tenant = apps.get_model('tenants', 'Tenant')
    claves = set(_DIRECCIONES)
    for tenant in Tenant.objects.all():
        if tenant.nombre.strip().lower() in claves:
            tenant.direccion = ''
            tenant.save(update_fields=['direccion'])


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0003_tenant_etiquetas_cortas'),
    ]

    operations = [
        migrations.RunPython(poblar_direcciones, revertir),
    ]
