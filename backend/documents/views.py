from collections import defaultdict
from datetime import date

from django.http import HttpResponse
from django.template.loader import render_to_string
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsTenantAdmin
from m00_onboarding.models import CicloNOM
from m06_results.models import ResultadoAplicacion

try:
    from weasyprint import HTML as WeasyHTML
    WEASYPRINT_OK = True
except Exception:
    WEASYPRINT_OK = False

# -------------------------------------------------------------------------
CAT_LABELS = {
    'bajo':     'Nulo / Bajo',
    'medio':    'Medio',
    'alto':     'Alto',
    'muy_alto': 'Muy alto',
}

GUIA_DESC = {
    'I':   'hasta 15 trabajadores',
    'III': '16 a 50 trabajadores',
    'V':   'más de 50 trabajadores',
}

RECOMENDACIONES_BASE = {
    'bajo': [
        ('Mantener y fortalecer las condiciones actuales del entorno organizacional.',
         'Medidas de control preventivo'),
        ('Continuar con programas de bienestar y comunicación interna.',
         'Buenas prácticas organizacionales'),
    ],
    'medio': [
        ('Revisar la distribución de carga de trabajo y ajustar en áreas de mayor presión.',
         'Factores propios de la actividad'),
        ('Implementar o reforzar canales de retroalimentación entre líderes y equipos.',
         'Liderazgo y relaciones en el trabajo'),
        ('Promover el uso de mecanismos de denuncia y atención a violencia laboral.',
         'Entorno organizacional'),
    ],
    'alto': [
        ('Diseñar e implementar un programa de intervención para reducir los niveles de riesgo identificados.',
         'Plan de acción correctivo'),
        ('Revisar las jornadas de trabajo y los mecanismos de control del tiempo.',
         'Organización del tiempo de trabajo'),
        ('Capacitar a mandos medios y supervisores en prevención de riesgos psicosociales.',
         'Liderazgo y relaciones en el trabajo'),
        ('Establecer un comité de seguridad y salud en el trabajo con seguimiento periódico.',
         'Estructura organizacional'),
    ],
    'muy_alto': [
        ('Activar de forma inmediata un programa de intervención con apoyo de especialistas.',
         'Intervención urgente'),
        ('Evaluar condiciones específicas de trabajo con personal de salud ocupacional.',
         'Salud ocupacional'),
        ('Implementar medidas de protección y apoyo psicológico para trabajadores en riesgo.',
         'Bienestar del trabajador'),
        ('Revisar políticas de contratación, estabilidad laboral y compensación.',
         'Entorno organizacional y seguridad laboral'),
        ('Documentar y dar seguimiento mensual a los indicadores de riesgo identificados.',
         'Seguimiento y control'),
    ],
}


def _get_recomendaciones(distribucion: dict) -> list:
    """Selecciona recomendaciones según el nivel de riesgo más alto encontrado."""
    recs = []
    for nivel in ('muy_alto', 'alto', 'medio', 'bajo'):
        if distribucion.get(nivel, 0) > 0:
            for texto, dominio in RECOMENDACIONES_BASE.get(nivel, []):
                recs.append({'nivel': nivel, 'texto': texto, 'dominio': dominio})
            break  # solo el nivel más alto
    # Siempre incluir la de bajo si hay riesgo bajo también
    if distribucion.get('bajo', 0) > 0 and recs and recs[0]['nivel'] != 'bajo':
        for texto, dominio in RECOMENDACIONES_BASE['bajo']:
            recs.append({'nivel': 'bajo', 'texto': texto, 'dominio': dominio})
    return recs


def _build_context(tenant, ciclo, resultados_qs) -> dict:
    resultados = list(
        resultados_qs.select_related(
            'aplicacion__trabajador',
            'aplicacion__cuestionario',
        ).prefetch_related('dominios__dominio')
    )

    total_apl = ciclo.aplicaciones.count() if hasattr(ciclo, 'aplicaciones') else 0
    total_comp = sum(1 for r in resultados if True)  # all in qs are already completados
    total_res = len(resultados)

    # Distribution
    dist_count = defaultdict(int)
    for r in resultados:
        dist_count[r.categoria] += 1

    total_dist = sum(dist_count.values()) or 1
    distribucion = [
        {
            'key':   k,
            'label': CAT_LABELS[k],
            'count': dist_count[k],
            'pct':   round(dist_count[k] / total_dist * 100),
        }
        for k in ('bajo', 'medio', 'alto', 'muy_alto')
    ]

    # Determine guia from first resultado
    guia = resultados[0].aplicacion.cuestionario.clave if resultados else '?'

    # Per-worker flat list
    workers = []
    for r in resultados:
        workers.append({
            'trabajador_nombre': r.aplicacion.trabajador.nombre_completo,
            'trabajador_area':   r.aplicacion.trabajador.area,
            'puntaje_total':     r.puntaje_total,
            'puntaje_max':       r.puntaje_max,
            'porcentaje':        r.puntaje_max and round(r.puntaje_total / r.puntaje_max * 100) or 0,
            'categoria':         r.categoria,
        })

    # Domain aggregates
    domain_data: dict[str, dict] = {}
    for r in resultados:
        for d in r.dominios.all():
            key = d.dominio_id
            if key not in domain_data:
                domain_data[key] = {
                    'nombre': d.dominio.nombre,
                    'puntajes': [],
                    'puntaje_max': d.puntaje_max,
                    'dist': defaultdict(int),
                }
            domain_data[key]['puntajes'].append(d.puntaje)
            domain_data[key]['dist'][d.categoria] += 1

    dominios_agregados = []
    for info in domain_data.values():
        puntajes = info['puntajes']
        avg = round(sum(puntajes) / len(puntajes)) if puntajes else 0
        pmax = info['puntaje_max']
        # Most common category
        cat_pred = max(info['dist'], key=info['dist'].get) if info['dist'] else 'bajo'
        dominios_agregados.append({
            'nombre':                info['nombre'],
            'puntaje_promedio':      avg,
            'puntaje_max':           pmax,
            'pct_promedio':          round(avg / pmax * 100) if pmax else 0,
            'categoria_predominante':cat_pred,
            'evaluados':             len(puntajes),
            'dist':                  dict(info['dist']),
        })

    pct_completado = round(total_res / total_apl * 100) if total_apl else 0

    return {
        'tenant':            tenant,
        'ciclo':             ciclo,
        'guia':              guia,
        'descripcion_guia':  GUIA_DESC.get(guia, ''),
        'fecha_generado':    date.today().strftime('%d de %B de %Y').replace(
                                 ' de enero ', ' de enero de '
                             ),
        'resumen': {
            'total_aplicaciones': total_apl,
            'total_completadas':  total_comp,
            'total_resultados':   total_res,
        },
        'pct_completado':    pct_completado,
        'distribucion':      distribucion,
        'resultados':        workers,
        'dominios_agregados':dominios_agregados,
        'recomendaciones':   _get_recomendaciones(dist_count),
    }


@api_view(['GET'])
@permission_classes([IsTenantAdmin])
def generar_informe(request):
    ciclo_id = request.query_params.get('ciclo_id')
    if not ciclo_id:
        return HttpResponse('ciclo_id requerido', status=400)

    tenant = request.user.tenant
    try:
        ciclo = CicloNOM.objects.get(id=ciclo_id, tenant=tenant)
    except CicloNOM.DoesNotExist:
        return HttpResponse('Ciclo no encontrado', status=404)

    resultados_qs = ResultadoAplicacion.objects.filter(
        aplicacion__tenant=tenant,
        aplicacion__ciclo=ciclo,
    )
    if not resultados_qs.exists():
        return HttpResponse(
            'No hay resultados calculados para este ciclo. '
            'Primero calcula el diagnóstico desde la sección de Resultados.',
            status=400,
        )

    ctx = _build_context(tenant, ciclo, resultados_qs)
    html_str = render_to_string('documents/informe_nom035.html', ctx, request=request)

    filename = f'informe_nom035_{tenant.nombre.replace(" ", "_")}_{ciclo.anio}.pdf'

    if WEASYPRINT_OK:
        pdf_bytes = WeasyHTML(string=html_str, base_url=request.build_absolute_uri('/')).write_pdf()
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
    else:
        # Fallback en local (Windows sin GTK): sirve el HTML con estilos de impresión
        response = HttpResponse(html_str + PRINT_HINT, content_type='text/html; charset=utf-8')

    return response


PRINT_HINT = """
<style>
  #print-hint {
    position: fixed; top: 0; left: 0; right: 0;
    background: #03c4ce; color: #fff; padding: 10px 20px;
    font-family: sans-serif; font-size: 13px;
    display: flex; align-items: center; justify-content: space-between;
    z-index: 9999; box-shadow: 0 2px 8px rgba(0,0,0,.2);
  }
  #print-hint button {
    background:#fff; color:#03c4ce; border:none; padding:6px 16px;
    border-radius:99px; font-weight:700; cursor:pointer;
  }
  @media print { #print-hint { display:none !important; } }
</style>
<div id="print-hint">
  Vista previa del informe — para generar el PDF usa Ctrl+P &rarr; "Guardar como PDF"
  <button onclick="window.print()">Imprimir / Guardar PDF</button>
</div>
"""
