"""Servicio de cálculo de resultados por ciclo.

Es el ÚNICO camino de persistencia de resultados: lo consume el endpoint
POST /resultados/calcular/ y también el cargador de fixtures de prueba
(documents.management.commands.cargar_fixture_prueba), de modo que cualquier
informe de prueba pasa exactamente por el mismo motor que producción.
"""
from m05_questionnaires.models import Aplicacion

from .models import (
    ResultadoAplicacion,
    ResultadoCategoria,
    ResultadoDimension,
    ResultadoDominio,
    ResultadoDominioOficial,
)
from .scoring import VERSION_MOTOR, calcular_resultado


def calcular_ciclo(tenant, ciclo) -> dict | None:
    """Calcula (o recalcula) los resultados de todas las aplicaciones
    completadas del ciclo. Devuelve el resumen de conteos, o None si el
    ciclo no tiene aplicaciones completadas."""
    aplicaciones = Aplicacion.objects.filter(
        tenant=tenant, ciclo=ciclo, estado='completado',
    ).select_related('cuestionario', 'trabajador').prefetch_related(
        'respuestas__pregunta',
        'cuestionario__dominios__preguntas',
    )

    if not aplicaciones.exists():
        return None

    calculadas = actualizadas = omitidas = requieren_revision = 0
    for aplicacion in aplicaciones:
        datos = calcular_resultado(aplicacion)
        if datos is None:
            ResultadoAplicacion.objects.filter(aplicacion=aplicacion).delete()
            omitidas += 1
            continue

        es_valido = datos.get('es_valido', True)
        detalle = {'validacion': datos.get('validacion')}
        if datos.get('guia_i'):
            detalle['guia_i'] = datos['guia_i']
        if datos.get('filtros'):
            detalle['filtros'] = datos['filtros']

        resultado, created = ResultadoAplicacion.objects.update_or_create(
            aplicacion=aplicacion,
            defaults={
                'puntaje_total':      datos['puntaje_total'] or 0,
                'puntaje_max':        datos['puntaje_max'] or 0,
                # Un cuestionario inválido NO se clasifica.
                'categoria':          datos['categoria'] if es_valido else 'sin_calificar',
                'requiere_atencion':  datos.get('requiere_atencion') if es_valido else None,
                'estatus_validacion': 'valido' if es_valido else 'requiere_revision',
                'version_motor':      datos.get('version_motor', VERSION_MOTOR),
                'hash_respuestas':    datos.get('hash_respuestas', ''),
                'detalle':            detalle,
            },
        )

        resultado.dominios.all().delete()
        resultado.dominios_oficiales.all().delete()
        resultado.categorias.all().delete()
        resultado.dimensiones.all().delete()

        if not es_valido:
            requieren_revision += 1
            continue

        ResultadoDominio.objects.bulk_create([
            ResultadoDominio(
                resultado   = resultado,
                dominio_id  = d['dominio_id'],
                puntaje     = d['puntaje'],
                puntaje_max = d['puntaje_max'],
                categoria   = d['categoria'],
            )
            for d in datos['dominios']
        ])

        ResultadoDominioOficial.objects.bulk_create([
            ResultadoDominioOficial(
                resultado   = resultado,
                clave       = d['clave'],
                nombre      = d['nombre'],
                orden       = d['orden'],
                puntaje     = d['puntaje'],
                puntaje_max = d['puntaje_max'],
                categoria   = d['categoria'],
            )
            for d in datos.get('dominios_oficiales', [])
        ])

        ResultadoCategoria.objects.bulk_create([
            ResultadoCategoria(
                resultado   = resultado,
                nombre      = c['nombre'],
                orden       = c['orden'],
                puntaje     = c['puntaje'],
                puntaje_max = c['puntaje_max'],
                categoria   = c['categoria'],
            )
            for c in datos.get('categorias', [])
        ])

        ResultadoDimension.objects.bulk_create([
            ResultadoDimension(
                resultado       = resultado,
                nombre          = d['nombre'],
                dominio_oficial = d['dominio_oficial'],
                orden           = d['orden'],
                puntaje         = d['puntaje'],
                puntaje_max     = d['puntaje_max'],
                pct             = d['pct'],
            )
            for d in datos.get('dimensiones', [])
        ])

        if created:
            calculadas += 1
        else:
            actualizadas += 1

    return {
        'calculadas':         calculadas,
        'actualizadas':       actualizadas,
        'omitidas':           omitidas,
        'requieren_revision': requieren_revision,
        'version_motor':      VERSION_MOTOR,
        'total':              calculadas + actualizadas,
    }
