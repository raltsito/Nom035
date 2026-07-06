import io
from collections import defaultdict
from datetime import date

from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from rest_framework import status as drf_status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import IsSuperAdmin, IsTenantAdmin
from core import xlsx_styles as xs
from m00_onboarding.models import CicloNOM, Trabajador
from m05_questionnaires.models import Aplicacion, Pregunta, RespuestaPregunta
from m06_results.models import ResultadoAplicacion
from m06_results.scoring import GUIA_III_GLOBAL, _categoria_por_rangos
from . import contenido_normativo as norm
from . import graficas as graf
from . import interpretaciones as interp
from .docx_builder import build_informe_diagnostico_docx, build_reporte_psicologico_docx
from .models import ReportePsicologico

# Cutoffs genéricos de porcentaje usados para clasificar agregados que el
# sistema deriva (categorías, dominios oficiales) y que no tienen una tabla
# de puntajes propia en la norma — la norma solo define cutoffs absolutos
# por dominio (`GUIA_III_DOMINIOS`). Mismo esquema ya usado en `_build_context`
# para el desglose por área.
_CUTOFFS_PCT = [(20, 'nulo'), (45, 'bajo'), (60, 'medio'), (75, 'alto')]


_MESES_ES = [
    '', 'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
    'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre',
]


def _fecha_es(d):
    """Formatea una fecha en español sin depender del locale del sistema."""
    return f'{d.day} de {_MESES_ES[d.month]} de {d.year}'


def _wrap(data, meta=None, errors=None, status_code=drf_status.HTTP_200_OK):
    return Response({'data': data, 'meta': meta or {}, 'errors': errors}, status=status_code)


def _tenant_para_ciclo(request, ciclo_id):
    """Resuelve el tenant a consultar: para super admins, el del ciclo elegido
    (pueden operar sobre cualquier tenant); para tenant_admin, siempre el suyo."""
    if request.user.is_super_admin and ciclo_id:
        ciclo = CicloNOM.objects.filter(id=ciclo_id).select_related('tenant').first()
        return ciclo.tenant if ciclo else None
    return request.user.tenant

try:
    from weasyprint import HTML as WeasyHTML
    WEASYPRINT_OK = True
except Exception:
    WEASYPRINT_OK = False

# -------------------------------------------------------------------------
# Categorías de riesgo Guía III (5 niveles oficiales)
DIST_KEYS = ('nulo', 'bajo', 'medio', 'alto', 'muy_alto')

CAT_LABELS = {
    'nulo':     'Nulo / Despreciable',
    'bajo':     'Bajo',
    'medio':    'Medio',
    'alto':     'Alto',
    'muy_alto': 'Muy alto',
}

# Cuadro 2 NOM-035-STPS-2018 — Acciones requeridas según el nivel de riesgo
ACCIONES_CUADRO2 = [
    ('nulo',
     'El riesgo resulta despreciable, por lo que no se requiere de medidas adicionales.'),
    ('bajo',
     'Es necesario revisar la política de prevención de riesgos psicosociales y '
     'programas para la prevención de los factores de riesgo psicosocial, la promoción '
     'de un entorno organizacional favorable y la prevención de la violencia laboral.'),
    ('medio',
     'Se requiere revisar y, en su caso, reforzar las acciones del programa de prevención '
     'de factores de riesgo psicosocial; realizar exámenes médicos y evaluaciones '
     'psicológicas a los trabajadores expuestos cuando existan signos o síntomas; y '
     'establecer un plan de acción con plazos y responsables definidos.'),
    ('alto',
     'Se requiere realizar el análisis de cada categoría y dominio para establecer las '
     'acciones de intervención correspondientes; revisar la política y reforzar el programa '
     'de prevención; efectuar exámenes médicos y evaluaciones psicológicas a los '
     'trabajadores expuestos; dar seguimiento mensual y canalizar a atención clínica a '
     'quienes lo requieran.'),
    ('muy_alto',
     'Se requiere realizar el análisis de cada categoría y dominio para establecer de '
     'inmediato las acciones de intervención y control; reforzar la aplicación de la '
     'política y del programa de prevención; realizar exámenes médicos y evaluaciones '
     'psicológicas a los trabajadores expuestos; y canalizar a atención clínica '
     'especializada de forma urgente, con seguimiento permanente.'),
]

# Interpretación narrativa del nivel de riesgo global de la organización
NIVEL_GLOBAL_TEXTO = {
    'nulo':
        'La organización presenta una exposición nula o despreciable a factores de riesgo '
        'psicosocial. Se recomienda mantener las prácticas actuales y reaplicar el '
        'cuestionario en el siguiente ciclo normativo.',
    'bajo':
        'Se detecta una exposición baja a factores de riesgo psicosocial. Existen áreas de '
        'mejora que conviene atender de forma preventiva para evitar que escalen en ciclos '
        'posteriores.',
    'medio':
        'Se detecta una exposición media a factores de riesgo psicosocial. Conforme al '
        'Apartado 8 de la NOM-035-STPS-2018, el patrón debe elaborar un plan de acción con '
        'medidas concretas, plazos y responsables asignados.',
    'alto':
        'Se detecta una exposición alta a factores de riesgo psicosocial. Se requieren '
        'acciones inmediatas de intervención organizacional, seguimiento mensual y '
        'evaluación individual de los trabajadores con puntajes más elevados.',
    'muy_alto':
        'Se detecta una exposición muy alta a factores de riesgo psicosocial. Constituye '
        'una situación crítica que requiere intervención urgente, atención médica y '
        'psicológica, y un programa de intervención con indicadores de seguimiento.',
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


def _clave_map(resultados) -> dict:
    """Asigna una clave anónima estable (T001, T002…) por trabajador,
    ordenada por nombre para que el mismo trabajador conserve su clave."""
    claves, seen = {}, []
    for r in sorted(resultados, key=lambda x: x.aplicacion.trabajador.nombre_completo):
        tid = r.aplicacion.trabajador_id
        if tid not in claves:
            seen.append(tid)
            claves[tid] = ''  # placeholder, se llena abajo
    return {tid: f'T{idx:03d}' for idx, tid in enumerate(seen, 1)}


def _build_context(tenant, ciclo, resultados_qs, anonimo=False) -> dict:
    resultados = list(
        resultados_qs.select_related(
            'aplicacion__trabajador',
            'aplicacion__cuestionario',
        ).prefetch_related('dominios__dominio')
    )

    res_iii = [r for r in resultados if r.aplicacion.cuestionario.clave == 'III']
    res_i   = [r for r in resultados if r.aplicacion.cuestionario.clave == 'I']

    clave_map = _clave_map(resultados) if anonimo else {}

    def _nombre(r):
        if anonimo:
            return clave_map.get(r.aplicacion.trabajador_id, 'T—')
        return r.aplicacion.trabajador.nombre_completo

    total_apl  = ciclo.aplicaciones.count() if hasattr(ciclo, 'aplicaciones') else 0
    total_res  = len(resultados)
    total_comp = total_res  # todos los del queryset ya tienen resultado calculado

    # ------------------------------------------------------------------
    # Guía III — distribución global (5 niveles) y nivel de riesgo global
    # ------------------------------------------------------------------
    dist_count = {k: 0 for k in DIST_KEYS}
    for r in res_iii:
        if r.categoria in dist_count:
            dist_count[r.categoria] += 1

    total_iii = len(res_iii)
    total_dist = sum(dist_count.values()) or 1
    distribucion = [
        {
            'key':   k,
            'label': CAT_LABELS[k],
            'count': dist_count[k],
            'pct':   round(dist_count[k] / total_dist * 100),
        }
        for k in DIST_KEYS
    ]

    # Nivel de riesgo global de la organización = promedio de puntajes globales
    promedio_global = round(sum(r.puntaje_total for r in res_iii) / total_iii) if total_iii else 0
    nivel_global = _categoria_por_rangos(promedio_global, GUIA_III_GLOBAL) if total_iii else 'nulo'

    # ------------------------------------------------------------------
    # Guía III — resultados individuales por trabajador
    # ------------------------------------------------------------------
    workers_iii = []
    for r in sorted(res_iii, key=lambda x: x.puntaje_total, reverse=True):
        workers_iii.append({
            'trabajador_nombre': _nombre(r),
            'trabajador_area':   r.aplicacion.trabajador.area or 'Sin área',
            'puntaje_total':     r.puntaje_total,
            'puntaje_max':       r.puntaje_max,
            'porcentaje':        round(r.puntaje_total / r.puntaje_max * 100) if r.puntaje_max else 0,
            'categoria':         r.categoria,
        })

    # ------------------------------------------------------------------
    # Guía I — Acontecimiento Traumático Severo (ATS)
    # ------------------------------------------------------------------
    guia_i_casos = []
    for r in res_i:
        if not r.requiere_atencion:
            continue
        acontecimiento = 0
        sintomas = 0
        secciones = []
        for d in r.dominios.all():
            if d.dominio.clave == 'D1':
                acontecimiento = d.puntaje
            else:
                sintomas += d.puntaje
            secciones.append({
                'clave':     d.dominio.clave,
                'nombre':    d.dominio.nombre,
                'positivos': d.puntaje,
                'total':     d.puntaje_max,
            })
        guia_i_casos.append({
            'trabajador_nombre': _nombre(r),
            'trabajador_area':   r.aplicacion.trabajador.area or 'Sin área',
            'acontecimiento':    acontecimiento,
            'sintomas':          sintomas,
            'secciones':         secciones,
        })

    requieren_i = sum(1 for r in res_i if r.requiere_atencion)
    guia_i = {
        'total':              len(res_i),
        'requieren_atencion': requieren_i,
        'sin_indicadores':    len(res_i) - requieren_i,
        'casos':              guia_i_casos,
    }

    # ------------------------------------------------------------------
    # Guía III — análisis por dominio (14) con nivel modal y por área
    # ------------------------------------------------------------------
    domain_map: dict[str, dict] = {}
    for r in res_iii:
        area = r.aplicacion.trabajador.area or 'Sin área'
        for d in r.dominios.all():
            if d.puntaje_max == 0:
                continue  # D13/D14 no aplicables a este trabajador
            clave = d.dominio.clave
            if clave not in domain_map:
                domain_map[clave] = {
                    'clave':       clave,
                    'nombre':      d.dominio.nombre,
                    'orden':       d.dominio.orden,
                    'pt':          0,
                    'pm':          0,
                    'dist':        {k: 0 for k in DIST_KEYS},
                    'areas':       defaultdict(lambda: {'pt': 0, 'pm': 0}),
                }
            info = domain_map[clave]
            info['pt'] += d.puntaje
            info['pm'] += d.puntaje_max
            if d.categoria in info['dist']:
                info['dist'][d.categoria] += 1
            info['areas'][area]['pt'] += d.puntaje
            info['areas'][area]['pm'] += d.puntaje_max

    dominios_agregados = []
    areas_set = set()
    for info in sorted(domain_map.values(), key=lambda x: x['orden']):
        evaluados = sum(info['dist'].values())
        avg = round(info['pt'] / evaluados, 1) if evaluados else 0
        pct = round(info['pt'] / info['pm'] * 100) if info['pm'] else 0
        cat_modal = max(info['dist'], key=info['dist'].get) if evaluados else 'nulo'
        por_area = {}
        for area_nombre, ae in info['areas'].items():
            areas_set.add(area_nombre)
            por_area[area_nombre] = {
                'pct':       round(ae['pt'] / ae['pm'] * 100) if ae['pm'] else 0,
                'categoria': _categoria_por_rangos(
                    round(ae['pt'] / ae['pm'] * 100) if ae['pm'] else 0,
                    [(20, 'nulo'), (45, 'bajo'), (60, 'medio'), (75, 'alto')],
                ),
            }
        dominios_agregados.append({
            'clave':                 info['clave'],
            'nombre':                info['nombre'],
            'puntaje_promedio':      avg,
            'puntaje_max':           round(info['pm'] / evaluados) if evaluados else 0,
            'pct_promedio':          pct,
            'categoria_predominante':cat_modal,
            'evaluados':             evaluados,
            'dist':                  info['dist'],
            'por_area':              por_area,
        })

    # ------------------------------------------------------------------
    # Análisis por área (nivel de riesgo promedio por departamento)
    # ------------------------------------------------------------------
    area_totales: dict[str, dict] = {}
    for r in res_iii:
        area = r.aplicacion.trabajador.area or 'Sin área'
        if area not in area_totales:
            area_totales[area] = {'suma': 0, 'n': 0, 'dist': {k: 0 for k in DIST_KEYS}}
        area_totales[area]['suma'] += r.puntaje_total
        area_totales[area]['n'] += 1
        if r.categoria in area_totales[area]['dist']:
            area_totales[area]['dist'][r.categoria] += 1

    areas_analisis = []
    for nombre, info in sorted(area_totales.items()):
        prom = round(info['suma'] / info['n']) if info['n'] else 0
        areas_analisis.append({
            'nombre':    nombre,
            'evaluados': info['n'],
            'promedio':  prom,
            'categoria': _categoria_por_rangos(prom, GUIA_III_GLOBAL),
            'dist':      info['dist'],
        })
    areas_analisis.sort(key=lambda a: a['promedio'], reverse=True)

    # ------------------------------------------------------------------
    # Acciones requeridas (Cuadro 2) — marcar niveles presentes
    # ------------------------------------------------------------------
    niveles_presentes = {k for k, v in dist_count.items() if v > 0}
    acciones = [
        {
            'key':      k,
            'label':    CAT_LABELS[k],
            'accion':   texto,
            'presente': k in niveles_presentes,
        }
        for k, texto in ACCIONES_CUADRO2
    ]

    pct_completado = round(total_res / total_apl * 100) if total_apl else 0

    return {
        'tenant':            tenant,
        'ciclo':             ciclo,
        'descripcion_guia':  GUIA_DESC.get('III', ''),
        'fecha_generado':    _fecha_es(date.today()),
        'resumen': {
            'total_aplicaciones': total_apl,
            'total_completadas':  total_comp,
            'total_resultados':   total_res,
            'total_guia_iii':     total_iii,
            'total_guia_i':       len(res_i),
        },
        'pct_completado':    pct_completado,
        'nivel_global':      nivel_global,
        'nivel_global_label':CAT_LABELS[nivel_global],
        'nivel_global_texto':NIVEL_GLOBAL_TEXTO[nivel_global],
        'promedio_global':   promedio_global,
        'distribucion':      distribucion,
        'resultados':        workers_iii,
        'guia_i':            guia_i,
        'dominios_agregados':dominios_agregados,
        'areas_analisis':    areas_analisis,
        'acciones':          acciones,
        'recomendaciones':   _get_recomendaciones(dist_count),
    }


def _pdf_response(html_str, filename, request):
    """Devuelve el HTML como PDF (WeasyPrint) o como vista imprimible (fallback local)."""
    if WEASYPRINT_OK:
        pdf_bytes = WeasyHTML(string=html_str, base_url=request.build_absolute_uri('/')).write_pdf()
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
    else:
        # Fallback en local (Windows sin GTK): sirve el HTML con estilos de impresión
        response = HttpResponse(html_str + PRINT_HINT, content_type='text/html; charset=utf-8')
    return response


@api_view(['GET'])
@permission_classes([IsTenantAdmin])
def descargar_informe_diagnostico(request):
    """Informe Diagnóstico NOM-035 completo (DOCX): portada, índice, 13
    secciones y gráficas — descarga directa, sin flujo de aprobación."""
    ciclo_id = request.query_params.get('ciclo_id')
    if not ciclo_id:
        return HttpResponse('ciclo_id requerido', status=400)

    tenant = _tenant_para_ciclo(request, ciclo_id)
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

    ctx = _build_psico_context(tenant, ciclo, resultados_qs, anonimo=False, informe_extendido=True)
    buf = build_informe_diagnostico_docx(ctx)

    filename = f'Informe_Diagnostico_NOM035_{tenant.nombre.replace(" ", "_")}_{ciclo.anio}.docx'
    response = HttpResponse(
        buf.read(),
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


# Orden de guías en las columnas del export de respuestas (igual al orden de
# aplicación real, ver `contenido_normativo.METODOLOGIA['orden_aplicacion']`).
_ORDEN_GUIA_RESPUESTAS = {'III': 0, 'I': 1, 'V': 2}


def _codigo_pregunta(pregunta):
    return f'{pregunta.dominio.cuestionario.clave}-{pregunta.dominio.clave}-P{pregunta.orden}'


def _valor_mostrado(respuesta):
    pregunta = respuesta.pregunta
    if pregunta.tipo_respuesta == 'si_no':
        if respuesta.valor == 1:
            return 'Sí'
        if respuesta.valor == 0:
            return 'No'
        return ''
    if pregunta.tipo_respuesta in ('texto', 'opcion'):
        return respuesta.valor_texto
    return respuesta.valor if respuesta.valor is not None else ''


@api_view(['GET'])
@permission_classes([IsTenantAdmin])
def exportar_respuestas_excel(request):
    """Excel con una fila por trabajador y una columna por pregunta (guías
    I/III/V) del ciclo elegido, más una hoja de referencia código→pregunta."""
    ciclo_id = request.query_params.get('ciclo_id')
    if not ciclo_id:
        return HttpResponse('ciclo_id requerido', status=400)

    tenant = _tenant_para_ciclo(request, ciclo_id)
    try:
        ciclo = CicloNOM.objects.get(id=ciclo_id, tenant=tenant)
    except CicloNOM.DoesNotExist:
        return HttpResponse('Ciclo no encontrado', status=404)

    preguntas = list(
        Pregunta.objects.filter(dominio__cuestionario__clave__in=_ORDEN_GUIA_RESPUESTAS)
        .select_related('dominio', 'dominio__cuestionario')
    )
    preguntas.sort(key=lambda p: (
        _ORDEN_GUIA_RESPUESTAS[p.dominio.cuestionario.clave], p.dominio.orden, p.orden,
    ))

    respuestas = (
        RespuestaPregunta.objects.filter(
            tenant=tenant,
            aplicacion__ciclo_id=ciclo_id,
            aplicacion__cuestionario__clave__in=_ORDEN_GUIA_RESPUESTAS,
        )
        .select_related('aplicacion__trabajador', 'pregunta')
    )

    valores = defaultdict(dict)
    trabajadores = {}
    for r in respuestas:
        trab = r.aplicacion.trabajador
        trabajadores[trab.id] = trab
        valores[trab.id][r.pregunta_id] = _valor_mostrado(r)

    trabajadores_ordenados = sorted(
        trabajadores.values(),
        key=lambda t: (t.apellido_paterno, t.apellido_materno, t.nombre),
    )

    wb = Workbook()
    ws = wb.active
    ws.title = 'Respuestas'
    ws.sheet_view.showGridLines = False

    cols_fijas = ['Folio', 'Nombre', 'Área']
    codigos = [_codigo_pregunta(p) for p in preguntas]
    headers = cols_fijas + codigos
    n_cols = len(headers)

    ws.merge_cells(f'A1:{get_column_letter(n_cols)}1')
    c = ws.cell(row=1, column=1,
                value=f'Respuestas NOM-035 — {tenant.nombre} — Ciclo {ciclo.anio}')
    c.fill = xs.fill(xs.NAVY)
    c.font = xs.font(bold=True, color=xs.WHITE, size=13)
    c.alignment = xs.center()
    ws.row_dimensions[1].height = 26

    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=2, column=col, value=h)
        cell.fill = xs.fill(xs.NAVY)
        cell.font = xs.font(bold=True, color=xs.WHITE, size=9)
        cell.alignment = xs.center(wrap=True)
        cell.border = xs.border()

    ws.column_dimensions['A'].width = 12
    ws.column_dimensions['B'].width = 32
    ws.column_dimensions['C'].width = 20
    for i in range(len(cols_fijas) + 1, n_cols + 1):
        ws.column_dimensions[get_column_letter(i)].width = 11

    for i, trab in enumerate(trabajadores_ordenados, 1):
        row = 2 + i
        bg = xs.LIGHT if i % 2 == 0 else xs.WHITE
        row_vals = [trab.num_empleado or '—', trab.nombre_completo, trab.area or '—']
        for p in preguntas:
            row_vals.append(valores.get(trab.id, {}).get(p.id, ''))
        for col, val in enumerate(row_vals, 1):
            cell = ws.cell(row=row, column=col, value=val)
            cell.fill = xs.fill(bg)
            cell.font = xs.font(bold=(col <= len(cols_fijas)))
            cell.alignment = xs.left() if col <= len(cols_fijas) else xs.center()
            cell.border = xs.border()

    ws2 = wb.create_sheet('Preguntas')
    ws2.sheet_view.showGridLines = False
    ws2.column_dimensions['A'].width = 18
    ws2.column_dimensions['B'].width = 90
    for col, h in enumerate(['Código', 'Texto de la pregunta'], 1):
        cell = ws2.cell(row=1, column=col, value=h)
        cell.fill = xs.fill(xs.NAVY)
        cell.font = xs.font(bold=True, color=xs.WHITE, size=10)
        cell.alignment = xs.center()
    for i, p in enumerate(preguntas, 1):
        bg = xs.LIGHT if i % 2 == 0 else xs.WHITE
        c1 = ws2.cell(row=1 + i, column=1, value=_codigo_pregunta(p))
        c1.fill, c1.font, c1.alignment = xs.fill(bg), xs.font(bold=True), xs.center()
        c2 = ws2.cell(row=1 + i, column=2, value=p.texto)
        c2.fill, c2.font, c2.alignment = xs.fill(bg), xs.font(), xs.left(wrap=True)

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)

    filename = f'respuestas_nom035_ciclo_{ciclo.anio}.xlsx'
    response = HttpResponse(
        buf.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
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


# ===========================================================================
# REPORTE PSICOLÓGICO (Sprint 6)
# ===========================================================================

def _distribucion_simple(valores):
    """Cuenta ocurrencias y devuelve [{label, count, pct}] ordenado desc."""
    counts = defaultdict(int)
    for v in valores:
        counts[v or 'Sin dato'] += 1
    total = sum(counts.values()) or 1
    return [
        {'label': k, 'count': v, 'pct': round(v / total * 100)}
        for k, v in sorted(counts.items(), key=lambda x: (-x[1], x[0]))
    ]


def _grupo_edad(edad):
    if edad is None:
        return 'Sin dato'
    if edad < 25:
        return '18–24 años'
    if edad < 35:
        return '25–34 años'
    if edad < 45:
        return '35–44 años'
    if edad < 55:
        return '45–54 años'
    return '55 años o más'


def _grupo_antiguedad(anios):
    if anios is None:
        return 'Sin dato'
    if anios < 1:
        return 'Menos de 1 año'
    if anios < 3:
        return '1 a 3 años'
    if anios < 5:
        return '3 a 5 años'
    if anios < 10:
        return '5 a 10 años'
    return 'Más de 10 años'


def _build_muestra(tenant, ciclo):
    """Distribución sociodemográfica (Guía V) de los trabajadores participantes."""
    trab_ids = (
        Aplicacion.objects.filter(tenant=tenant, ciclo=ciclo)
        .values_list('trabajador_id', flat=True).distinct()
    )
    trabajadores = list(Trabajador.objects.filter(id__in=trab_ids))

    return {
        'total':      len(trabajadores),
        'sexo':       _distribucion_simple(
            [t.get_sexo_display() if t.sexo else None for t in trabajadores]),
        'edad':       _distribucion_simple(
            [_grupo_edad(t.edad) for t in trabajadores]),
        'estudios':   _distribucion_simple(
            [t.get_nivel_estudios_display() if t.nivel_estudios else None for t in trabajadores]),
        'puesto':     _distribucion_simple(
            [t.tipo_puesto or None for t in trabajadores]),
        'jornada':    _distribucion_simple(
            [t.get_tipo_jornada_display() if t.tipo_jornada else None for t in trabajadores]),
        'rotacion':   _distribucion_simple(
            [('Sí' if t.rotacion_turnos else 'No') if t.rotacion_turnos is not None else None
             for t in trabajadores]),
        'antiguedad': _distribucion_simple(
            [_grupo_antiguedad(t.experiencia_empresa_anios) for t in trabajadores]),
    }


def _build_tasas_respuesta(tenant, ciclo):
    """Tasa de respuesta (completadas / aplicadas) por guía."""
    base = Aplicacion.objects.filter(tenant=tenant, ciclo=ciclo)
    etiquetas = [
        ('I',   'Guía I — Acontecimientos Traumáticos Severos'),
        ('III', 'Guía III — Factores de Riesgo Psicosocial'),
        ('V',   'Guía V — Datos del Trabajador'),
    ]
    tasas = []
    for clave, etiqueta in etiquetas:
        total = base.filter(cuestionario__clave=clave).count()
        if not total:
            continue
        comp = base.filter(cuestionario__clave=clave, estado='completado').count()
        tasas.append({
            'guia':        etiqueta,
            'total':       total,
            'completadas': comp,
            'pct':         round(comp / total * 100) if total else 0,
        })
    return tasas


URGENCIA_POR_NIVEL = {
    'muy_alto': 'Inmediata',
    'alto':     'A mediano plazo',
    'medio':    'Preventiva',
}


def _recomendacion_dominio(clave):
    """Extrae la acción concreta ('Se recomienda…') del texto clínico del dominio."""
    texto = interp.DOMINIO_INTERPRETACION.get(clave, {}).get('alto', '')
    idx = texto.find('Se recomienda')
    return texto[idx:] if idx != -1 else texto


def _recomendaciones_desde_dominios(dominios_prioritarios):
    """Genera recomendaciones concretas a partir de los dominios en nivel Alto / Muy alto,
    ordenadas por urgencia y citando el dominio que las origina."""
    orden = {'muy_alto': 0, 'alto': 1}
    recs = []
    for dom in sorted(dominios_prioritarios,
                      key=lambda d: (orden.get(d['categoria_predominante'], 9), -d['pct_promedio'])):
        nivel = dom['categoria_predominante']
        recs.append({
            'nivel':    nivel,
            'urgencia': URGENCIA_POR_NIVEL.get(nivel, 'A mediano plazo'),
            'texto':    _recomendacion_dominio(dom['clave']),
            'dominio':  f"{dom['clave']} — {dom['nombre']}",
        })
    return recs


def _recomendaciones_extendidas(dominios_oficiales_agregados):
    """Recomendaciones extensas (5-7 bullets por dominio, con intro), solo
    para el Informe Diagnóstico extendido (`informe_extendido=True`) — usa
    `norm.RECOMENDACIONES_DOMINIO` en vez de la extracción de una frase que
    consume el flujo borrador/aprobar. Se listan los dominios con intervención
    real (`pct_intervencion > 0`), de mayor a menor porcentaje."""
    recs = []
    for dom in sorted(dominios_oficiales_agregados, key=lambda d: -d['pct_intervencion']):
        if dom['pct_intervencion'] <= 0:
            continue
        contenido = norm.RECOMENDACIONES_DOMINIO.get(dom['nombre'])
        if not contenido:
            continue
        recs.append({
            'dominio':          dom['nombre'],
            'pct_intervencion': dom['pct_intervencion'],
            'intro':            contenido['intro'],
            'bullets':          contenido['bullets'],
        })
    return recs


def _build_graficas_informe(ctx):
    """PNGs (matplotlib) del Informe Diagnóstico extendido. Solo se calculan
    cuando `informe_extendido=True` — nunca para el flujo borrador/aprobar
    existente, para no alterar su comportamiento ya validado."""
    graficas = {}

    dist_no_cero = [d for d in ctx['distribucion'] if d['count'] > 0]
    if dist_no_cero:
        graficas['distribucion'] = graf.chart_pie(
            [d['label'] for d in dist_no_cero],
            [d['count'] for d in dist_no_cero],
        )

    graficas['categorias'] = {
        c['nombre']: graf.chart_nivel_dist(c['nombre'], c['dist'], c['evaluados'])
        for c in ctx['categorias_agregadas']
    }
    graficas['dominios'] = {
        d['nombre']: graf.chart_nivel_dist(d['nombre'], d['dist'], d['evaluados'])
        for d in ctx['dominios_oficiales_agregados']
    }

    graficas['muestra'] = {}
    for tabla in ctx['muestra_tablas']:
        datos = tabla['datos']
        if not datos:
            continue
        labels = [d['label'] for d in datos]
        counts = [d['count'] for d in datos]
        if len(datos) <= 3:
            graficas['muestra'][tabla['col']] = graf.chart_pie(labels, counts)
        else:
            total = sum(counts) or 1
            pcts = [c / total * 100 for c in counts]
            graficas['muestra'][tabla['col']] = graf.chart_barh(labels, pcts, counts)

    return graficas


def _riesgo_por_grupo(res_iii, keyfn):
    """Nivel de riesgo promedio (Guía III) agrupado por un atributo del trabajador."""
    groups = {}
    for r in res_iii:
        k = keyfn(r.aplicacion.trabajador) or 'Sin dato'
        g = groups.setdefault(k, {'suma': 0, 'n': 0})
        g['suma'] += r.puntaje_total
        g['n'] += 1
    out = []
    for label, g in groups.items():
        prom = round(g['suma'] / g['n']) if g['n'] else 0
        out.append({
            'label':     label,
            'evaluados': g['n'],
            'promedio':  prom,
            'categoria': _categoria_por_rangos(prom, GUIA_III_GLOBAL),
        })
    out.sort(key=lambda x: -x['promedio'])
    return out


def _agregar_por_grupo(por_trabajador, orden):
    """Reduce un dict {trabajador_id: {grupo: {pt, pm}}} a una lista ordenada de
    agregados por grupo (categoría o dominio oficial), clasificando a cada
    trabajador con los cutoffs genéricos de porcentaje."""
    grupos = defaultdict(lambda: {'dist': {k: 0 for k in DIST_KEYS}, 'pct_sum': 0, 'n': 0})
    for items in por_trabajador.values():
        for nombre, vals in items.items():
            if not vals['pm']:
                continue
            pct = round(vals['pt'] / vals['pm'] * 100)
            nivel = _categoria_por_rangos(pct, _CUTOFFS_PCT)
            g = grupos[nombre]
            g['dist'][nivel] += 1
            g['pct_sum'] += pct
            g['n'] += 1

    salida = []
    for nombre in orden:
        g = grupos.get(nombre)
        if not g or not g['n']:
            continue
        requieren = g['dist']['alto'] + g['dist']['muy_alto']
        salida.append({
            'nombre':                nombre,
            'evaluados':             g['n'],
            'dist':                  g['dist'],
            'pct_promedio':          round(g['pct_sum'] / g['n']),
            'categoria_predominante':max(g['dist'], key=g['dist'].get),
            'requieren_atencion':    requieren,
            'pct_intervencion':      round(requieren / g['n'] * 100),
        })
    return salida


def _build_jerarquia_categorias(res_iii):
    """Agrega los 14 dominios calificados (D1-D14) en la jerarquía oficial
    Categoría (5) → Dominio (Tabla 6, Guía III), sumando puntaje/puntaje_max
    por trabajador y reclasificando con cutoffs de porcentaje. No fabrica
    datos: solo reagrupa los puntajes por dominio ya calculados en
    `m06_results.scoring`."""
    cat_por_trabajador = defaultdict(lambda: defaultdict(lambda: {'pt': 0, 'pm': 0}))
    dom_por_trabajador = defaultdict(lambda: defaultdict(lambda: {'pt': 0, 'pm': 0}))
    for r in res_iii:
        tid = r.aplicacion.trabajador_id
        for d in r.dominios.all():
            if not d.puntaje_max:
                continue
            categoria = norm.DOMINIO_CATEGORIA.get(d.dominio.clave)
            dominio_of = norm.DOMINIO_OFICIAL_DE.get(d.dominio.clave)
            if categoria:
                cat_por_trabajador[tid][categoria]['pt'] += d.puntaje
                cat_por_trabajador[tid][categoria]['pm'] += d.puntaje_max
            if dominio_of:
                dom_por_trabajador[tid][dominio_of]['pt'] += d.puntaje
                dom_por_trabajador[tid][dominio_of]['pm'] += d.puntaje_max

    orden_categorias = [c for c, _ in norm.CATEGORIA_ESTRUCTURA]
    orden_dominios = [dom for _, doms in norm.CATEGORIA_ESTRUCTURA for dom, _ in doms]
    categorias_agregadas = _agregar_por_grupo(cat_por_trabajador, orden_categorias)
    dominios_oficiales_agregados = _agregar_por_grupo(dom_por_trabajador, orden_dominios)
    return categorias_agregadas, dominios_oficiales_agregados


def _build_conclusiones(ctx):
    """Texto de conclusiones (sección 10), generado a partir de los datos ya
    calculados del ciclo — mismo formato narrativo que el estándar LEAR."""
    riesgo_alto = sum(c['count'] for c in ctx['distribucion'] if c['key'] in ('alto', 'muy_alto'))
    total_iii = ctx['resumen']['total_guia_iii']
    pct_riesgo = round(riesgo_alto / total_iii * 100) if total_iii else 0

    categorias_destacadas = [
        c for c in sorted(ctx['categorias_agregadas'], key=lambda x: -x['pct_intervencion'])
        if c['pct_intervencion'] > 0
    ][:4]
    dominios_destacados = [
        d for d in sorted(ctx['dominios_oficiales_agregados'], key=lambda x: -x['pct_intervencion'])
        if d['pct_intervencion'] > 0
    ][:4]

    return {
        'muestra':               total_iii,
        'poblacion':             ctx['tenant'].num_trabajadores,
        'riesgo_alto':           riesgo_alto,
        'pct_riesgo':            pct_riesgo,
        'categorias_destacadas': categorias_destacadas,
        'dominios_destacados':   dominios_destacados,
    }


def _build_anexos(res_iii, res_i):
    """Tablas de anexos (13.1-13.4), siempre identificadas por folio (T001…)
    independientemente del modo anónimo del cuerpo del reporte — así se
    presentan en el estándar de referencia."""
    trabajadores = {r.aplicacion.trabajador_id: r.aplicacion.trabajador for r in (list(res_iii) + list(res_i))}
    claves = {
        tid: f'T{idx:03d}'
        for idx, tid in enumerate(
            sorted(trabajadores, key=lambda t_id: trabajadores[t_id].nombre_completo), 1)
    }
    atencion_guia_i = {r.aplicacion.trabajador_id: r.requiere_atencion for r in res_i}

    ats_final = []
    for r in sorted(res_iii, key=lambda x: -x.puntaje_total):
        tid = r.aplicacion.trabajador_id
        ats_final.append({
            'clave':              claves.get(tid, '—'),
            'ats':                ('Atención requerida' if atencion_guia_i.get(tid)
                                    else 'Sin indicadores' if tid in atencion_guia_i else 'No aplicado'),
            'calificacion_final': r.puntaje_total,
            'nivel_final':        r.categoria,
        })

    orden_categorias = [c for c, _ in norm.CATEGORIA_ESTRUCTURA]
    orden_dominios = [dom for _, doms in norm.CATEGORIA_ESTRUCTURA for dom, _ in doms]

    categorias_filas, dominios_filas = [], []
    for r in sorted(res_iii, key=lambda x: claves.get(x.aplicacion.trabajador_id, '')):
        tid = r.aplicacion.trabajador_id
        cat_acc = defaultdict(lambda: {'pt': 0, 'pm': 0})
        dom_acc = defaultdict(lambda: {'pt': 0, 'pm': 0})
        for d in r.dominios.all():
            if not d.puntaje_max:
                continue
            categoria = norm.DOMINIO_CATEGORIA.get(d.dominio.clave)
            dominio_of = norm.DOMINIO_OFICIAL_DE.get(d.dominio.clave)
            if categoria:
                cat_acc[categoria]['pt'] += d.puntaje
                cat_acc[categoria]['pm'] += d.puntaje_max
            if dominio_of:
                dom_acc[dominio_of]['pt'] += d.puntaje
                dom_acc[dominio_of]['pm'] += d.puntaje_max

        def _nivel(acc, nombre):
            v = acc.get(nombre)
            if not v or not v['pm']:
                return None
            return _categoria_por_rangos(round(v['pt'] / v['pm'] * 100), _CUTOFFS_PCT)

        categorias_filas.append({
            'clave':   claves.get(tid, '—'),
            'niveles': [_nivel(cat_acc, c) for c in orden_categorias],
        })
        dominios_filas.append({
            'clave':   claves.get(tid, '—'),
            'niveles': [_nivel(dom_acc, d) for d in orden_dominios],
        })

    return {
        'ats_final':           ats_final,
        'categorias_columnas': orden_categorias,
        'categorias_filas':    categorias_filas,
        'dominios_columnas':   orden_dominios,
        'dominios_filas':      dominios_filas,
        'agrupacion':          norm.TABLA_AGRUPACION_DOMINIOS,
    }


def _build_psico_context(tenant, ciclo, resultados_qs, anonimo, informe_extendido=False):
    """`informe_extendido=True` agrega gráficas (matplotlib) y recomendaciones
    extensas por dominio — solo lo activa `descargar_informe_diagnostico`
    (botón "Descargar informe"). El flujo borrador/aprobar existente nunca lo
    pasa, así que su contenido/comportamiento queda intacto."""
    ctx = _build_context(tenant, ciclo, resultados_qs, anonimo=anonimo)

    resultados_lista = list(resultados_qs.select_related(
        'aplicacion__trabajador', 'aplicacion__cuestionario').prefetch_related('dominios__dominio'))
    res_iii = [r for r in resultados_lista if r.aplicacion.cuestionario.clave == 'III']
    res_i = [r for r in resultados_lista if r.aplicacion.cuestionario.clave == 'I']
    riesgo_por_grupo = {
        'sexo':    _riesgo_por_grupo(res_iii, lambda t: t.get_sexo_display() if t.sexo else None),
        'edad':    _riesgo_por_grupo(res_iii, lambda t: _grupo_edad(t.edad)),
        'puesto':  _riesgo_por_grupo(res_iii, lambda t: t.tipo_puesto or None),
        'jornada': _riesgo_por_grupo(res_iii, lambda t: t.get_tipo_jornada_display() if t.tipo_jornada else None),
    }

    # Interpretación clínica del nivel de riesgo global (versión extendida)
    ctx['nivel_global_texto'] = interp.NIVEL_GLOBAL[ctx['nivel_global']]

    # Enriquecer cada dominio con qué mide + interpretación clínica si es prioritario
    for dom in ctx['dominios_agregados']:
        meta = interp.DOMINIO_INTERPRETACION.get(dom['clave'], {})
        dom['mide'] = meta.get('mide', '')
        prioritario = dom['categoria_predominante'] in ('alto', 'muy_alto')
        dom['prioritario'] = prioritario
        dom['interpretacion'] = meta.get('alto', '') if prioritario else ''

    dominios_prioritarios = [d for d in ctx['dominios_agregados'] if d['prioritario']]

    # Dimensiones (9.4) = los 14 dominios D1-D14 ya calificados, etiquetados con
    # el dominio oficial (Tabla 6) al que pertenecen — es el nivel de
    # desagregación más fino con el que cuenta el sistema.
    dimensiones = [
        {**dom, 'dominio_oficial': norm.DOMINIO_OFICIAL_DE.get(dom['clave'], dom['nombre'])}
        for dom in ctx['dominios_agregados']
    ]

    categorias_agregadas, dominios_oficiales_agregados = _build_jerarquia_categorias(res_iii)

    # Guía I — texto interpretativo según haya o no casos positivos
    if ctx['guia_i']['requieren_atencion'] > 0:
        guia_i_texto = interp.GUIA_I_TEXTO_POSITIVO
    else:
        guia_i_texto = interp.GUIA_I_TEXTO_SIN_INDICADORES

    muestra = _build_muestra(tenant, ciclo)
    muestra_tablas = [
        {'titulo': 'Distribución por sexo',            'col': 'Sexo',             'datos': muestra['sexo']},
        {'titulo': 'Distribución por grupo de edad',   'col': 'Grupo de edad',    'datos': muestra['edad']},
        {'titulo': 'Distribución por nivel de estudios','col': 'Nivel de estudios','datos': muestra['estudios']},
        {'titulo': 'Distribución por tipo de puesto',  'col': 'Tipo de puesto',   'datos': muestra['puesto']},
        {'titulo': 'Distribución por tipo de jornada', 'col': 'Tipo de jornada',  'datos': muestra['jornada']},
        {'titulo': 'Rotación de turnos',               'col': 'Realiza rotación', 'datos': muestra['rotacion']},
        {'titulo': 'Antigüedad en la empresa',         'col': 'Antigüedad',       'datos': muestra['antiguedad']},
    ]
    riesgo_tablas = [
        {'titulo': 'Por sexo',           'col': 'Sexo',          'datos': riesgo_por_grupo['sexo']},
        {'titulo': 'Por grupo de edad',  'col': 'Grupo de edad', 'datos': riesgo_por_grupo['edad']},
        {'titulo': 'Por tipo de puesto', 'col': 'Tipo de puesto','datos': riesgo_por_grupo['puesto']},
        {'titulo': 'Por tipo de jornada','col': 'Tipo de jornada','datos': riesgo_por_grupo['jornada']},
    ]

    sexo_dist = {d['label']: d['count'] for d in muestra['sexo']}

    ctx.update({
        'anonimo':               anonimo,
        # Se llena solo al aprobar, vía _inyectar_validacion_revisor() — nunca es texto libre.
        'validacion':            None,
        'marco':                 interp.MARCO_NORMATIVO,
        'guia_i_definicion':     interp.GUIA_I_DEFINICION,
        'guia_i_texto':          guia_i_texto,
        'limitaciones':          interp.LIMITACIONES,
        'muestra':               muestra,
        'muestra_tablas':        muestra_tablas,
        'tasas_respuesta':       _build_tasas_respuesta(tenant, ciclo),
        'dominios_prioritarios': dominios_prioritarios,
        'dimensiones':           dimensiones,
        'categorias_agregadas':  categorias_agregadas,
        'dominios_oficiales_agregados': dominios_oficiales_agregados,
        'riesgo_por_grupo':      riesgo_por_grupo,
        'riesgo_tablas':         riesgo_tablas,
        # Recomendaciones derivadas de los dominios prioritarios (sustituye las genéricas)
        'recomendaciones':       _recomendaciones_desde_dominios(dominios_prioritarios),
        # ---- Contenido normativo fijo + datos del centro de trabajo (Fase 2) ----
        'datos_centro_trabajo': {
            'nombre':    tenant.nombre,
            'direccion': tenant.direccion,
            'giro':      tenant.giro,
        },
        'objetivo_general':      norm.OBJETIVO_GENERAL,
        'objetivos_especificos': norm.OBJETIVOS_ESPECIFICOS,
        'definiciones':          norm.DEFINICIONES,
        'justificacion_muestra': {
            'intro':     norm.JUSTIFICACION_MUESTRA_INTRO,
            'poblacion': tenant.num_trabajadores,
            'muestra':   ctx['resumen']['total_guia_iii'],
            'hombres':   sexo_dist.get('Masculino', 0),
            'mujeres':   sexo_dist.get('Femenino', 0),
        },
        'metodologia': norm.METODOLOGIA,
    })
    ctx['conclusiones'] = _build_conclusiones(ctx)
    ctx['anexos'] = _build_anexos(res_iii, res_i)

    if informe_extendido:
        ctx['acciones_generales'] = norm.ACCIONES_GENERALES
        ctx['recomendaciones_extendidas'] = _recomendaciones_extendidas(dominios_oficiales_agregados)
        ctx['graficas'] = _build_graficas_informe(ctx)

    return ctx


def _inyectar_validacion_revisor(ctx, revisor):
    """Sobreescribe la sección de cierre con los datos reales del revisor que
    aprueba el reporte. Solo se llama al aprobar — el borrador nunca lleva
    estos datos."""
    ctx['validacion'] = {
        'nombre_revisor':   revisor.nombre_completo,
        'cedula_revisor':   revisor.cedula_profesional,
        'fecha_aprobacion': _fecha_es(timezone.localdate()),
    }
    return ctx


def _resultados_qs_o_none(tenant, ciclo):
    qs = ResultadoAplicacion.objects.filter(aplicacion__tenant=tenant, aplicacion__ciclo=ciclo)
    return qs if qs.exists() else None


@api_view(['POST'])
@permission_classes([IsSuperAdmin])
def reporte_psicologico_borrador(request):
    ciclo_id = request.data.get('ciclo_id') or request.query_params.get('ciclo_id')
    if not ciclo_id:
        return _wrap(None, errors={'detail': 'ciclo_id requerido'}, status_code=400)

    anonimo_raw = request.data.get('anonimo', request.query_params.get('anonimo', False))
    anonimo = str(anonimo_raw).lower() in ('true', '1', 'yes')

    try:
        ciclo = CicloNOM.objects.select_related('tenant').get(id=ciclo_id)
    except CicloNOM.DoesNotExist:
        return _wrap(None, errors={'detail': 'Ciclo no encontrado'}, status_code=404)
    tenant = ciclo.tenant

    reporte, _created = ReportePsicologico.objects.get_or_create(
        tenant=tenant, ciclo=ciclo, defaults={'estado': ReportePsicologico.ESTADO_BORRADOR},
    )
    if reporte.is_aprobado:
        return _wrap(None, errors={'detail': 'El reporte ya fue aprobado y es inmutable.'}, status_code=409)

    resultados_qs = _resultados_qs_o_none(tenant, ciclo)
    if resultados_qs is None:
        return _wrap(None, errors={'detail': 'No hay resultados calculados para este ciclo.'}, status_code=400)

    ctx = _build_psico_context(tenant, ciclo, resultados_qs, anonimo)

    reporte.estado = ReportePsicologico.ESTADO_BORRADOR
    reporte.anonimo = anonimo
    reporte.generado_por = request.user
    reporte.generado_en = timezone.now()
    reporte.save()

    docx_buf = build_reporte_psicologico_docx(ctx)
    filename = f'borrador_reporte_psicologico_{tenant.nombre.replace(" ", "_")}_{ciclo.anio}.docx'
    response = HttpResponse(
        docx_buf.read(),
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@api_view(['POST'])
@permission_classes([IsSuperAdmin])
def reporte_psicologico_aprobar(request):
    ciclo_id = request.data.get('ciclo_id') or request.query_params.get('ciclo_id')
    if not ciclo_id:
        return _wrap(None, errors={'detail': 'ciclo_id requerido'}, status_code=400)

    try:
        ciclo = CicloNOM.objects.select_related('tenant').get(id=ciclo_id)
    except CicloNOM.DoesNotExist:
        return _wrap(None, errors={'detail': 'Ciclo no encontrado'}, status_code=404)
    tenant = ciclo.tenant

    if tenant.consultor_id != request.user.id:
        return _wrap(
            None,
            errors={'detail': 'Solo el consultor asignado a esta empresa puede aprobar su reporte.'},
            status_code=403,
        )
    if not request.user.cedula_profesional.strip():
        return _wrap(
            None,
            errors={'detail': 'No tienes una cédula profesional registrada. Contacta al administrador del sistema.'},
            status_code=403,
        )

    try:
        reporte = ReportePsicologico.objects.get(tenant=tenant, ciclo=ciclo)
    except ReportePsicologico.DoesNotExist:
        return _wrap(
            None,
            errors={'detail': 'No existe un borrador para este ciclo. Genera el borrador primero.'},
            status_code=404,
        )
    if reporte.is_aprobado:
        return _wrap(None, errors={'detail': 'El reporte ya fue aprobado previamente.'}, status_code=409)

    resultados_qs = _resultados_qs_o_none(tenant, ciclo)
    if resultados_qs is None:
        return _wrap(None, errors={'detail': 'No hay resultados calculados para este ciclo.'}, status_code=400)

    ctx = _build_psico_context(tenant, ciclo, resultados_qs, reporte.anonimo)
    ctx = _inyectar_validacion_revisor(ctx, request.user)
    html_final = render_to_string('documents/reporte_psicologico.html', ctx, request=request)

    reporte.estado = ReportePsicologico.ESTADO_APROBADO
    reporte.revisor = request.user
    reporte.nombre_revisor = request.user.nombre_completo
    reporte.cedula_revisor = request.user.cedula_profesional
    reporte.fecha_aprobacion = timezone.now()
    reporte.contenido_html_final = html_final
    reporte.save()

    return _wrap({
        'estado':           reporte.estado,
        'nombre_revisor':   reporte.nombre_revisor,
        'fecha_aprobacion': reporte.fecha_aprobacion,
    })


@api_view(['GET'])
@permission_classes([IsTenantAdmin])
def reporte_psicologico_descargar(request):
    ciclo_id = request.query_params.get('ciclo_id')
    if not ciclo_id:
        return HttpResponse('ciclo_id requerido', status=400)

    tenant = _tenant_para_ciclo(request, ciclo_id)
    try:
        ciclo = CicloNOM.objects.get(id=ciclo_id, tenant=tenant)
    except CicloNOM.DoesNotExist:
        return HttpResponse('Ciclo no encontrado', status=404)

    try:
        reporte = ReportePsicologico.objects.get(tenant=tenant, ciclo=ciclo)
    except ReportePsicologico.DoesNotExist:
        return HttpResponse('Aún no se ha generado un reporte psicológico para este ciclo.', status=404)

    if not reporte.is_aprobado:
        return HttpResponse('El reporte psicológico está en revisión y aún no ha sido aprobado.', status=409)

    filename = f'reporte_psicologico_{tenant.nombre.replace(" ", "_")}_{ciclo.anio}.pdf'
    return _pdf_response(reporte.contenido_html_final, filename, request)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reporte_psicologico_estado(request):
    ciclo_id = request.query_params.get('ciclo_id')
    if not ciclo_id:
        return _wrap(None, errors={'detail': 'ciclo_id requerido'}, status_code=400)

    if request.user.is_super_admin:
        try:
            ciclo = CicloNOM.objects.select_related('tenant').get(id=ciclo_id)
        except CicloNOM.DoesNotExist:
            return _wrap(None, errors={'detail': 'Ciclo no encontrado'}, status_code=404)
        tenant = ciclo.tenant
    else:
        tenant = request.user.tenant
        try:
            ciclo = CicloNOM.objects.get(id=ciclo_id, tenant=tenant)
        except CicloNOM.DoesNotExist:
            return _wrap(None, errors={'detail': 'Ciclo no encontrado'}, status_code=404)

    reporte = ReportePsicologico.objects.filter(tenant=tenant, ciclo=ciclo).first()
    puede_aprobar = bool(
        request.user.is_super_admin
        and tenant.consultor_id == request.user.id
        and request.user.cedula_profesional.strip()
    )
    return _wrap({
        'existe':                 reporte is not None,
        'estado':                 reporte.estado if reporte else None,
        'anonimo':                reporte.anonimo if reporte else None,
        'generado_en':            reporte.generado_en if reporte else None,
        'nombre_revisor':         reporte.nombre_revisor if reporte else '',
        'fecha_aprobacion':       reporte.fecha_aprobacion if reporte else None,
        'puede_generar_borrador': bool(request.user.is_super_admin),
        'puede_aprobar':          puede_aprobar,
    })
