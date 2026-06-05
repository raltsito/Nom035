from collections import defaultdict
from datetime import date

from django.http import HttpResponse
from django.template.loader import render_to_string
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsTenantAdmin
from m00_onboarding.models import CicloNOM, Trabajador
from m05_questionnaires.models import Aplicacion
from m06_results.models import ResultadoAplicacion
from m06_results.scoring import GUIA_III_GLOBAL, _categoria_por_rangos
from . import interpretaciones as interp

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
        'fecha_generado':    date.today().strftime('%d de %B de %Y'),
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
    return _pdf_response(html_str, filename, request)


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


def _build_psico_context(tenant, ciclo, resultados_qs, anonimo, responsable):
    ctx = _build_context(tenant, ciclo, resultados_qs, anonimo=anonimo)

    res_iii = [
        r for r in resultados_qs.select_related(
            'aplicacion__trabajador', 'aplicacion__cuestionario')
        if r.aplicacion.cuestionario.clave == 'III'
    ]
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

    ctx.update({
        'anonimo':               anonimo,
        'responsable':           responsable,
        'marco':                 interp.MARCO_NORMATIVO,
        'guia_i_definicion':     interp.GUIA_I_DEFINICION,
        'guia_i_texto':          guia_i_texto,
        'limitaciones':          interp.LIMITACIONES,
        'muestra':               muestra,
        'muestra_tablas':        muestra_tablas,
        'tasas_respuesta':       _build_tasas_respuesta(tenant, ciclo),
        'dominios_prioritarios': dominios_prioritarios,
        'riesgo_por_grupo':      riesgo_por_grupo,
        'riesgo_tablas':         riesgo_tablas,
        # Recomendaciones derivadas de los dominios prioritarios (sustituye las genéricas)
        'recomendaciones':       _recomendaciones_desde_dominios(dominios_prioritarios),
    })
    return ctx


@api_view(['GET'])
@permission_classes([IsTenantAdmin])
def generar_reporte_psicologico(request):
    ciclo_id = request.query_params.get('ciclo_id')
    if not ciclo_id:
        return HttpResponse('ciclo_id requerido', status=400)

    anonimo     = request.query_params.get('anonimo') in ('true', '1', 'yes')
    responsable = (request.query_params.get('responsable') or '').strip()

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

    ctx = _build_psico_context(tenant, ciclo, resultados_qs, anonimo, responsable)
    html_str = render_to_string('documents/reporte_psicologico.html', ctx, request=request)

    sufijo = '_anonimo' if anonimo else ''
    filename = f'reporte_psicologico_{tenant.nombre.replace(" ", "_")}_{ciclo.anio}{sufijo}.pdf'
    return _pdf_response(html_str, filename, request)
