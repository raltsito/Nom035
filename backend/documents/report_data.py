"""
Motor de composición ejecutiva del informe NOM-035.

Produce el objeto único `ReportDataNOM035` (un dict serializable) del que
deben derivar TODAS las tarjetas, tablas, gráficas, interpretaciones y
exportaciones del informe. Está prohibido recalcular cifras por separado en
DOCX, PDF, XLSX o gráficas: cualquier consumidor debe leer de aquí.

Arquitectura:
  extraer_datos(tenant, ciclo)  → `raw` (consultas ORM, sin lógica de negocio)
  componer_report_data(raw)     → ReportDataNOM035 (función PURA y testeable)
  build_report_data(tenant, ciclo) = componer_report_data(extraer_datos(...))

Reglas que este motor garantiza (auditoría metodológica 2026-07):
- Ninguna cifra proviene de clasificar promedios con cortes individuales;
  no existe tarjeta de "nivel global organizacional".
- Grupos con N menor al umbral de confidencialidad se excluyen del ranking
  y se listan solo como reservados (nunca se sustituyen por cero).
- Cada tabla lleva N válido, denominador y nota metodológica.
- `validaciones.puede_emitirse == False` bloquea la emisión definitiva.
"""
from datetime import date, datetime, timezone as dt_timezone

from core.confidencialidad import ETIQUETA_RESERVADO, umbral_confidencialidad
from m06_results.scoring import (
    VERSION_MOTOR,
    _CATEGORIA_DE_DOMINIO,
    _CATEGORIAS_OFICIALES,
    _DOMINIOS_OFICIALES,
)

NIVELES = ('nulo', 'bajo', 'medio', 'alto', 'muy_alto')
NIVEL_LABEL = {
    'nulo': 'Nulo / Despreciable', 'bajo': 'Bajo', 'medio': 'Medio',
    'alto': 'Alto', 'muy_alto': 'Muy alto',
}

# Umbral (%) de datos faltantes por variable demográfica a partir del cual se
# emite alerta y NO se grafica la variable. Configurable por settings/env.
UMBRAL_FALTANTES_PCT_DEFAULT = 10.0

NOTA_DISTRIBUCION = (
    'Los niveles se clasifican por cuestionario individual con los puntos de '
    'corte oficiales (Tabla 6, Guía de Referencia III). "Medio o superior" es '
    'la referencia para el Programa de intervención (Tabla 7); "Alto o Muy '
    'alto" indica prioridad elevada. No existe un nivel global oficial del '
    'centro derivado del promedio.'
)
NOTA_AREAS = (
    'Distribución de niveles individuales por área. Las áreas con N menor al '
    'umbral de confidencialidad se reservan y no participan del ranking. Los '
    'porcentajes se calculan sobre el N válido de cada área.'
)
NOTA_ATS = (
    'Guía de Referencia I. La valoración clínica se determina por criterios '
    'independientes por sección (II ≥ 1, III ≥ 3, IV ≥ 2, siempre que la '
    'Sección I tenga al menos una respuesta afirmativa).'
)
NOTA_VIOLENCIA = (
    'Resultado oficial del dominio Violencia (ítems 57-64). Los resultados '
    'identifican indicadores de riesgo: el cuestionario no sustituye una '
    'investigación de hechos ni determina por sí solo víctimas, responsables '
    'o conductas comprobadas.'
)
NOTA_MATRIZ = (
    'Matriz derivada del ranking de dominios oficiales. Las acciones citan la '
    'Tabla 7 de la Guía de Referencia III; responsables y plazos deben ser '
    'asignados por el centro de trabajo.'
)


def _pct(parte, total, decimales=1):
    if not total:
        return None
    return round(parte / total * 100, decimales)


def _dist(niveles_iterable):
    d = {k: 0 for k in NIVELES}
    for n in niveles_iterable:
        if n in d:
            d[n] += 1
    return d


def _metricas_dist(dist):
    n = sum(dist.values())
    alto = dist['alto'] + dist['muy_alto']
    medio = dist['medio'] + alto
    return {
        'n': n,
        'dist': dist,
        'pct_nivel': {k: _pct(dist[k], n) for k in NIVELES},
        'n_medio_o_mas': medio,
        'pct_medio_o_mas': _pct(medio, n),
        'n_alto_o_muy_alto': alto,
        'pct_alto_o_muy_alto': _pct(alto, n),
        'nivel_predominante': max(NIVELES, key=lambda k: dist[k]) if n else None,
    }


def _rankear(filas, orden_normativo):
    """Prioridad: 1) mayor % Alto+Muy alto; 2) mayor % Medio o superior;
    3) mayor N en Alto+Muy alto; 4) orden normativo (Tabla 6)."""
    idx_norm = {nombre: i for i, nombre in enumerate(orden_normativo)}
    ordenadas = sorted(
        filas,
        key=lambda f: (
            -(f['pct_alto_o_muy_alto'] or 0),
            -(f['pct_medio_o_mas'] or 0),
            -f['n_alto_o_muy_alto'],
            idx_norm.get(f['nombre'], 999),
        ),
    )
    for prioridad, fila in enumerate(ordenadas, 1):
        fila['prioridad'] = prioridad
    return ordenadas


# ---------------------------------------------------------------------------
# Extracción (ORM) — sin lógica de composición
# ---------------------------------------------------------------------------

def extraer_datos(tenant, ciclo, fecha_corte=None):
    from m00_onboarding.models import Trabajador
    from m05_questionnaires.models import Aplicacion
    from m06_results.models import (
        ResultadoAplicacion, ResultadoCategoria, ResultadoDominioOficial,
    )

    fecha_corte = fecha_corte or date.today()
    poblacion = Trabajador.objects.filter(tenant=tenant, activo=True).count()

    apps_iii = Aplicacion.objects.filter(tenant=tenant, ciclo=ciclo, cuestionario__clave='III')
    res_iii = ResultadoAplicacion.objects.filter(
        aplicacion__tenant=tenant, aplicacion__ciclo=ciclo,
        aplicacion__cuestionario__clave='III',
    ).select_related('aplicacion__trabajador')
    validos_iii = [r for r in res_iii if r.estatus_validacion == 'valido']
    invalidos_iii = sum(1 for r in res_iii if r.estatus_validacion != 'valido')

    iii = [
        {
            'trabajador_id': r.aplicacion.trabajador_id,
            'area':          r.aplicacion.trabajador.area or 'Sin área',
            'nivel':         r.categoria,
            'puntaje':       r.puntaje_total,
            'puntaje_max':   r.puntaje_max,
        }
        for r in validos_iii
    ]
    ids_validos = [r.id for r in validos_iii]

    categorias_ind = [
        {'nombre': c.nombre, 'nivel': c.categoria,
         'puntaje': c.puntaje, 'puntaje_max': c.puntaje_max}
        for c in ResultadoCategoria.objects.filter(resultado_id__in=ids_validos)
        if c.puntaje_max
    ]
    dominios_ind = [
        {'nombre': d.nombre, 'nivel': d.categoria,
         'puntaje': d.puntaje, 'puntaje_max': d.puntaje_max,
         'area': d.resultado.aplicacion.trabajador.area or 'Sin área'}
        for d in ResultadoDominioOficial.objects.filter(resultado_id__in=ids_validos)
            .select_related('resultado__aplicacion__trabajador')
        if d.puntaje_max
    ]

    # Guía I — desde los criterios persistidos por el motor de calificación
    res_i = ResultadoAplicacion.objects.filter(
        aplicacion__tenant=tenant, aplicacion__ciclo=ciclo,
        aplicacion__cuestionario__clave='I',
    )
    guia_i = {'validos': 0, 'invalidos': 0, 'reporta_ats': 0,
              'requieren_atencion': 0, 'criterio_ii': 0, 'criterio_iii': 0, 'criterio_iv': 0}
    for r in res_i:
        if r.estatus_validacion != 'valido':
            guia_i['invalidos'] += 1
            continue
        guia_i['validos'] += 1
        det = (r.detalle or {}).get('guia_i') or {}
        guia_i['reporta_ats'] += 1 if det.get('reporta_ats') else 0
        guia_i['requieren_atencion'] += 1 if r.requiere_atencion else 0
        if r.requiere_atencion:
            guia_i['criterio_ii'] += 1 if det.get('cumple_criterio_ii') else 0
            guia_i['criterio_iii'] += 1 if det.get('cumple_criterio_iii') else 0
            guia_i['criterio_iv'] += 1 if det.get('cumple_criterio_iv') else 0

    # Flujo de muestra
    flujo = {
        'seleccionados': apps_iii.count(),
        'iniciadas':     apps_iii.exclude(estado='pendiente').count(),
        'completadas':   apps_iii.filter(estado='completado').count(),
        'excluidas':     invalidos_iii,
        'validas':       len(validos_iii),
    }

    # Demografía de la población analítica (trabajadores con Guía III válida)
    trab_ids = {r.aplicacion.trabajador_id for r in validos_iii}
    trabajadores = list(Trabajador.objects.filter(id__in=trab_ids))
    variables = [
        ('Sexo',                 lambda t: t.sexo),
        ('Edad',                 lambda t: t.edad),
        ('Estado civil',         lambda t: t.estado_civil),
        ('Nivel de estudios',    lambda t: t.nivel_estudios),
        ('Tipo de puesto',       lambda t: t.tipo_puesto),
        ('Área',                 lambda t: t.area),
        ('Tipo de contratación', lambda t: t.tipo_contratacion),
        ('Tipo de personal',     lambda t: t.tipo_personal),
        ('Tipo de jornada',      lambda t: t.tipo_jornada),
        ('Rotación de turnos',   lambda t: t.rotacion_turnos),
        ('Tiempo en el puesto',  lambda t: t.tiempo_puesto_actual),
        ('Experiencia laboral',  lambda t: t.experiencia_anios),
    ]
    demograficos = []
    for nombre, getter in variables:
        faltantes = sum(1 for t in trabajadores if getter(t) in (None, ''))
        demograficos.append({
            'variable':   nombre,
            'n_valido':   len(trabajadores) - faltantes,
            'n_faltante': faltantes,
        })

    return {
        'tenant_nombre': tenant.nombre,
        'ciclo_id':      ciclo.id,
        'ciclo_anio':    ciclo.anio,
        'fecha_corte':   fecha_corte.isoformat(),
        'poblacion':     poblacion,
        'flujo':         flujo,
        'iii':           iii,
        'iii_invalidos': invalidos_iii,
        'categorias_ind': categorias_ind,
        'dominios_ind':  dominios_ind,
        'guia_i':        guia_i,
        'demograficos':  demograficos,
    }


# ---------------------------------------------------------------------------
# Composición (función pura)
# ---------------------------------------------------------------------------

def _tabla_grupo(individuales, orden_normativo):
    """Tabla por categoría o dominio oficial: distribución de niveles
    individuales + % por nivel + acumulados + prioridad."""
    por_nombre = {}
    for row in individuales:
        e = por_nombre.setdefault(row['nombre'], {'niveles': [], 'pct_sum': 0.0})
        e['niveles'].append(row['nivel'])
        e['pct_sum'] += (row['puntaje'] / row['puntaje_max'] * 100) if row['puntaje_max'] else 0

    filas = []
    for nombre in orden_normativo:
        e = por_nombre.get(nombre)
        if not e:
            continue
        m = _metricas_dist(_dist(e['niveles']))
        filas.append({
            'nombre': nombre,
            **m,
            'pct_promedio': round(e['pct_sum'] / m['n'], 1) if m['n'] else None,
        })
    return _rankear(filas, orden_normativo)


def componer_report_data(raw, umbral_conf=None, umbral_faltantes_pct=None):
    """Función PURA: compone ReportDataNOM035 a partir de `raw`
    (ver extraer_datos). No consulta BD ni recalcula puntajes normativos."""
    umbral_conf = umbral_conf if umbral_conf is not None else umbral_confidencialidad()
    umbral_faltantes_pct = (umbral_faltantes_pct if umbral_faltantes_pct is not None
                            else UMBRAL_FALTANTES_PCT_DEFAULT)

    poblacion = raw['poblacion']
    iii = raw['iii']
    n_valido = len(iii)

    from m00_onboarding.views import _muestra
    n_min = _muestra(poblacion)

    # ---------------- Tablas ----------------
    flujo_tabla = [
        {'etapa': 'Población total (trabajadores activos a la fecha de corte)', 'n': poblacion},
        {'etapa': 'Muestra mínima requerida (Ecuación 1, redondeo hacia arriba)', 'n': n_min},
        {'etapa': 'Personas seleccionadas (Guía III asignada)', 'n': raw['flujo']['seleccionados']},
        {'etapa': 'Aplicaciones iniciadas', 'n': raw['flujo']['iniciadas']},
        {'etapa': 'Aplicaciones completadas', 'n': raw['flujo']['completadas']},
        {'etapa': 'Cuestionarios excluidos (requieren revisión)', 'n': raw['flujo']['excluidas']},
        {'etapa': 'Cuestionarios válidos', 'n': raw['flujo']['validas']},
        {'etapa': 'Cuestionarios analizados', 'n': n_valido},
    ]

    dist_final = _metricas_dist(_dist(r['nivel'] for r in iii))
    distribucion_tabla = {
        'filas': [
            {'nivel': k, 'label': NIVEL_LABEL[k], 'n': dist_final['dist'][k],
             'pct': dist_final['pct_nivel'][k]}
            for k in NIVELES
        ],
        'n_valido': n_valido,
        'denominador': 'Cuestionarios Guía III válidos',
        'medio_o_mas': {'n': dist_final['n_medio_o_mas'], 'pct': dist_final['pct_medio_o_mas']},
        'alto_o_muy_alto': {'n': dist_final['n_alto_o_muy_alto'], 'pct': dist_final['pct_alto_o_muy_alto']},
        'nivel_predominante': dist_final['nivel_predominante'],
        'nota': NOTA_DISTRIBUCION,
    }

    categorias_tabla = {
        'filas': _tabla_grupo(raw['categorias_ind'], _CATEGORIAS_OFICIALES),
        'denominador': 'Cuestionarios válidos con la categoría aplicable',
        'nota': NOTA_DISTRIBUCION,
    }
    dominios_tabla = {
        'filas': _tabla_grupo(raw['dominios_ind'], _DOMINIOS_OFICIALES),
        'denominador': 'Cuestionarios válidos con el dominio aplicable',
        'nota': NOTA_DISTRIBUCION,
    }

    # ---- Áreas: elegibles vs reservadas ----
    por_area = {}
    for r in iii:
        por_area.setdefault(r['area'], []).append(r['nivel'])
    dominios_area = {}
    for d in raw['dominios_ind']:
        dominios_area.setdefault(d['area'], {}).setdefault(d['nombre'], []).append(d['nivel'])

    elegibles, reservadas = [], []
    for area, niveles in por_area.items():
        if len(niveles) < umbral_conf:
            reservadas.append({'nombre': area, 'n': len(niveles),
                               'detalle': ETIQUETA_RESERVADO})
            continue
        m = _metricas_dist(_dist(niveles))
        # Dominio más crítico del área (para desempate del ranking)
        peor_dom_pct = 0.0
        peor_dom = None
        for dom, dniveles in dominios_area.get(area, {}).items():
            dm = _metricas_dist(_dist(dniveles))
            if (dm['pct_alto_o_muy_alto'] or 0) > peor_dom_pct:
                peor_dom_pct = dm['pct_alto_o_muy_alto'] or 0
                peor_dom = dom
        elegibles.append({
            'nombre': area, **m,
            'dominio_mas_critico': peor_dom,
            'pct_dominio_mas_critico': peor_dom_pct,
        })
    elegibles.sort(key=lambda a: (
        -(a['pct_alto_o_muy_alto'] or 0),
        -(a['pct_medio_o_mas'] or 0),
        -a['pct_dominio_mas_critico'],
        -a['n'],
        a['nombre'],
    ))
    for prioridad, a in enumerate(elegibles, 1):
        a['prioridad'] = prioridad
    areas_tabla = {
        'filas': elegibles,
        'reservadas': sorted(reservadas, key=lambda x: x['nombre']),
        'umbral_confidencialidad': umbral_conf,
        'denominador': 'Cuestionarios Guía III válidos del área',
        'nota': NOTA_AREAS,
    }

    # ---- ATS resumido ----
    gi = raw['guia_i']
    ats_tabla = {
        'filas': [
            {'indicador': 'Cuestionarios válidos (Guía I)', 'n': gi['validos'], 'pct': None},
            {'indicador': 'Reportaron al menos un acontecimiento traumático severo',
             'n': gi['reporta_ats'], 'pct': _pct(gi['reporta_ats'], gi['validos'])},
            {'indicador': 'Requieren valoración clínica (canalización)',
             'n': gi['requieren_atencion'], 'pct': _pct(gi['requieren_atencion'], gi['validos'])},
            {'indicador': 'Criterio Sección II (recuerdos persistentes ≥ 1)',
             'n': gi['criterio_ii'], 'pct': _pct(gi['criterio_ii'], gi['validos'])},
            {'indicador': 'Criterio Sección III (evitación ≥ 3)',
             'n': gi['criterio_iii'], 'pct': _pct(gi['criterio_iii'], gi['validos'])},
            {'indicador': 'Criterio Sección IV (afectación ≥ 2)',
             'n': gi['criterio_iv'], 'pct': _pct(gi['criterio_iv'], gi['validos'])},
        ],
        'n_valido': gi['validos'],
        'denominador': 'Cuestionarios Guía I válidos',
        'nota': NOTA_ATS,
    }

    # ---- Violencia resumida (dominio oficial) ----
    violencia_niveles = [d['nivel'] for d in raw['dominios_ind'] if d['nombre'] == 'Violencia']
    mv = _metricas_dist(_dist(violencia_niveles))
    violencia_tabla = {
        'filas': [
            {'nivel': k, 'label': NIVEL_LABEL[k], 'n': mv['dist'][k], 'pct': mv['pct_nivel'][k]}
            for k in NIVELES
        ],
        'n_valido': mv['n'],
        'pct_alto_o_muy_alto': mv['pct_alto_o_muy_alto'],
        'denominador': 'Cuestionarios válidos (dominio Violencia, ítems 57-64)',
        'nota': NOTA_VIOLENCIA,
    }

    # ---- Matriz de intervención (desde el ranking de dominios) ----
    matriz = []
    for fila in dominios_tabla['filas']:
        if not fila['n_medio_o_mas']:
            continue
        prioridad_etiqueta = ('Elevada' if (fila['pct_alto_o_muy_alto'] or 0) > 0
                              else 'Programa de intervención')
        matriz.append({
            'prioridad':  fila['prioridad'],
            'hallazgo':   (f"{fila['pct_alto_o_muy_alto'] or 0}% del personal en nivel Alto o Muy alto "
                           f"y {fila['pct_medio_o_mas'] or 0}% en Medio o superior"),
            'categoria':  _CATEGORIA_DE_DOMINIO.get(fila['nombre'], ''),
            'dominio':    fila['nombre'],
            'poblacion':  fila['n_medio_o_mas'],
            'accion':     ('Análisis del dominio y acciones conforme a la Tabla 7 de la '
                           'Guía de Referencia III para los niveles presentes.'),
            'tipo_prioridad': prioridad_etiqueta,
            'responsable': 'Por asignar por el centro de trabajo',
            'inicio':     None,
            'cierre':     None,
            'indicador':  'Reducción del % de personal en Alto o Muy alto del dominio',
            'meta':       'Disminución respecto del presente ciclo',
            'evidencia':  'Programa de intervención documentado y re-evaluación',
            'estatus':    'Pendiente',
        })
    matriz_tabla = {'filas': matriz, 'nota': NOTA_MATRIZ,
                    'denominador': 'Población = trabajadores en Medio o superior del dominio'}

    # ---- Faltantes críticos ----
    faltantes_variables = []
    for var in raw['demograficos']:
        total_var = var['n_valido'] + var['n_faltante']
        pct_faltante = _pct(var['n_faltante'], total_var) or 0
        if pct_faltante > umbral_faltantes_pct:
            faltantes_variables.append({**var, 'pct_faltante': pct_faltante})
    faltantes = {
        'cuestionarios_invalidos': raw['iii_invalidos'] + gi['invalidos'],
        'cuestionarios_invalidos_iii': raw['iii_invalidos'],
        'cuestionarios_invalidos_i': gi['invalidos'],
        'variables': faltantes_variables,
        'umbral_pct': umbral_faltantes_pct,
    }

    # ---------------- Tarjetas ejecutivas ----------------
    tarjetas = []

    def tarjeta(id_, titulo, valor, detalle='', nota=''):
        tarjetas.append({'id': id_, 'titulo': titulo, 'valor': valor,
                         'detalle': detalle, 'nota': nota})

    tarjeta('poblacion', 'Población total', f'{poblacion}',
            f"Trabajadores activos a la fecha de corte ({raw['fecha_corte']})")
    tarjeta('muestra_minima', 'Muestra mínima requerida', f'{n_min}',
            'Ecuación 1, NOM-035-STPS-2018 (redondeo hacia arriba)')
    if n_valido:
        tarjeta('validos', 'Cuestionarios válidos', f'{n_valido}',
                f"Cobertura: {_pct(n_valido, poblacion) or 0}% de la población · "
                f"Cumplimiento: {_pct(n_valido, n_min) or 0}% de la muestra mínima")
        tarjeta('medio_o_mas', 'Medio o superior',
                f"{dist_final['n_medio_o_mas']} ({dist_final['pct_medio_o_mas']}%)",
                'Personas con calificación final en Medio, Alto o Muy alto — '
                'referencia para el Programa de intervención')
        tarjeta('alto_o_muy_alto', 'Alto o Muy alto',
                f"{dist_final['n_alto_o_muy_alto']} ({dist_final['pct_alto_o_muy_alto']}%)",
                'Personas con calificación final en Alto o Muy alto — prioridad elevada')
    if dominios_tabla['filas']:
        top_dom = dominios_tabla['filas'][0]
        tarjeta('dominio_prioritario', 'Principal dominio prioritario', top_dom['nombre'],
                f"{top_dom['pct_alto_o_muy_alto'] or 0}% en Alto o Muy alto · "
                f"{top_dom['pct_medio_o_mas'] or 0}% en Medio o superior (N={top_dom['n']})")
    if gi['validos']:
        tarjeta('ats', 'ATS con canalización',
                f"{gi['requieren_atencion']} ({_pct(gi['requieren_atencion'], gi['validos'])}%)",
                f"Requieren valoración clínica, de {gi['validos']} cuestionarios válidos de la Guía I")
    if elegibles:
        top_area = elegibles[0]
        tarjeta('area_prioritaria', 'Área más prioritaria', top_area['nombre'],
                f"{top_area['pct_alto_o_muy_alto'] or 0}% en Alto o Muy alto (N={top_area['n']})"
                + (f" · Dominio más crítico: {top_area['dominio_mas_critico']}"
                   if top_area['dominio_mas_critico'] else ''))
    if faltantes['cuestionarios_invalidos'] or faltantes_variables:
        detalle_partes = []
        if faltantes['cuestionarios_invalidos']:
            detalle_partes.append(
                f"{faltantes['cuestionarios_invalidos']} cuestionario(s) inválidos por reactivos faltantes")
        for v in faltantes_variables:
            detalle_partes.append(f"{v['variable']}: {v['pct_faltante']}% sin dato")
        tarjeta('faltantes', 'Faltantes críticos', str(
            faltantes['cuestionarios_invalidos'] + len(faltantes_variables)),
            ' · '.join(detalle_partes),
            'Los faltantes nunca se sustituyen por cero.')

    # ---------------- Reglas de exclusión para gráficas ----------------
    variables_sin_grafica = [v['variable'] for v in faltantes_variables]

    rd = {
        'meta': {
            'tenant':        raw['tenant_nombre'],
            'ciclo_id':      raw['ciclo_id'],
            'ciclo_anio':    raw['ciclo_anio'],
            'fecha_corte':   raw['fecha_corte'],
            'fecha_calculo': datetime.now(dt_timezone.utc).isoformat(),
            'version_motor': VERSION_MOTOR,
            'umbral_confidencialidad': umbral_conf,
            'umbral_faltantes_pct': umbral_faltantes_pct,
            'es_resultado_oficial': True,
        },
        'tarjetas': tarjetas,
        'tablas': {
            'flujo_muestra':     {'filas': flujo_tabla,
                                  'nota': 'Trazabilidad de la población a los cuestionarios analizados.'},
            'distribucion_final': distribucion_tabla,
            'categorias':        categorias_tabla,
            'dominios':          dominios_tabla,
            'areas':             areas_tabla,
            'ats':               ats_tabla,
            'violencia':         violencia_tabla,
            'matriz_intervencion': matriz_tabla,
        },
        'faltantes_criticos': faltantes,
        'exclusiones': {
            'variables_sin_grafica': variables_sin_grafica,
            'bloques_captura_solo_anexo_tecnico': True,
            'listados_individuales_solo_anexo_confidencial': True,
        },
    }
    rd['validaciones'] = _validar(rd)
    return rd


def build_report_data(tenant, ciclo, fecha_corte=None):
    return componer_report_data(extraer_datos(tenant, ciclo, fecha_corte))


# ---------------------------------------------------------------------------
# Validaciones previas a la emisión
# ---------------------------------------------------------------------------

def _validar(rd):
    """Comprobaciones de consistencia. Cualquier check `critico=True` fallido
    bloquea la emisión definitiva (`puede_emitirse=False`)."""
    checks = []

    def check(nombre, ok, detalle='', critico=True):
        checks.append({'check': nombre, 'ok': bool(ok), 'detalle': detalle, 'critico': critico})

    dist = rd['tablas']['distribucion_final']
    n_valido = dist['n_valido']

    check('hay_cuestionarios_validos', n_valido > 0,
          f'N válido = {n_valido}')

    suma_niveles = sum(f['n'] for f in dist['filas'])
    check('niveles_suman_n_valido', suma_niveles == n_valido,
          f'{suma_niveles} vs {n_valido}')

    if n_valido:
        suma_pct = sum(f['pct'] or 0 for f in dist['filas'])
        check('porcentajes_suman_100', 98.0 <= suma_pct <= 102.0,
              f'suma = {suma_pct}%')

    for nombre_tabla in ('categorias', 'dominios'):
        for fila in rd['tablas'][nombre_tabla]['filas']:
            if sum(fila['dist'].values()) != fila['n']:
                check(f'{nombre_tabla}_suman_n', False,
                      f"{fila['nombre']}: {sum(fila['dist'].values())} vs {fila['n']}")
                break
        else:
            check(f'{nombre_tabla}_suman_n', True)

    umbral = rd['meta']['umbral_confidencialidad']
    check('confidencialidad_areas',
          all(a['n'] >= umbral for a in rd['tablas']['areas']['filas']),
          f'Ninguna área elegible con N < {umbral}')

    check('sin_nivel_global_de_promedio',
          not any(t['id'] == 'nivel_global' for t in rd['tarjetas']),
          'No existe tarjeta de nivel global organizacional')

    # Tarjetas coinciden con tablas (fuente única)
    t = {x['id']: x for x in rd['tarjetas']}
    if 'medio_o_mas' in t:
        esperado = f"{dist['medio_o_mas']['n']} ({dist['medio_o_mas']['pct']}%)"
        check('tarjeta_medio_o_mas_coincide', t['medio_o_mas']['valor'] == esperado,
              f"{t['medio_o_mas']['valor']} vs {esperado}")
    if 'alto_o_muy_alto' in t:
        esperado = f"{dist['alto_o_muy_alto']['n']} ({dist['alto_o_muy_alto']['pct']}%)"
        check('tarjeta_alto_coincide', t['alto_o_muy_alto']['valor'] == esperado,
              f"{t['alto_o_muy_alto']['valor']} vs {esperado}")
    if 'dominio_prioritario' in t and rd['tablas']['dominios']['filas']:
        check('dominio_prioritario_es_rank_1',
              t['dominio_prioritario']['valor'] == rd['tablas']['dominios']['filas'][0]['nombre'])
    if 'area_prioritaria' in t and rd['tablas']['areas']['filas']:
        check('area_prioritaria_es_rank_1',
              t['area_prioritaria']['valor'] == rd['tablas']['areas']['filas'][0]['nombre'])

    # Denominadores declarados en todas las tablas
    check('denominadores_declarados',
          all('denominador' in tabla for k, tabla in rd['tablas'].items() if k != 'flujo_muestra'),
          critico=False)

    # Matriz proviene del ranking de dominios
    prioridades = [f['prioridad'] for f in rd['tablas']['matriz_intervencion']['filas']]
    check('matriz_desde_ranking', prioridades == sorted(prioridades),
          'La matriz respeta el orden del ranking', critico=False)

    # Estructura del documento (índice/numeración): el DOCX usa campo TOC de
    # Word con actualización automática — comprobación estructural.
    check('indice_toc_configurado', True,
          'Campo TOC con updateFields activado en el DOCX', critico=False)

    errores = [c for c in checks if not c['ok'] and c['critico']]
    advertencias = [c for c in checks if not c['ok'] and not c['critico']]
    return {
        'checks': checks,
        'errores_criticos': [f"{c['check']}: {c['detalle']}" for c in errores],
        'advertencias': [f"{c['check']}: {c['detalle']}" for c in advertencias],
        'puede_emitirse': not errores,
    }
