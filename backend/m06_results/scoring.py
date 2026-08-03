"""
Motor de calificación NOM-035-STPS-2018 — ÚNICA fuente de verdad normativa.

Constantes verificadas contra el texto oficial (DOF 23-oct-2018,
https://asinom.stps.gob.mx/upload/nom/48.pdf) el 2026-07-14:

Guía I  — Acontecimiento Traumático Severo (ATS). Resultado binario (GR.I,
          incisos a y b): requiere atención clínica si Sección I ≥ 1 "Sí" Y
          al menos uno de: Sección II ≥ 1, Sección III ≥ 3, Sección IV ≥ 2.
          Cada sección tiene su propio umbral independiente (no se suman).
Guía III — Factores de riesgo psicosocial (72 ítems). La calificación oficial
           es por SUMA de puntajes (Tabla 5: recodificación; Tabla 6:
           integración de ítems) en cuatro niveles de agregación:
           - Calificación final (Cfinal) con cortes <50/<75/<99/<140/≥140.
           - 5 categorías oficiales (Ccat), con cortes propios.
           - 10 dominios oficiales (Cdom), con cortes propios.
           - 25 dimensiones: la NOM NO define cortes por dimensión; aquí se
             calculan solo como indicador descriptivo (suma, máximo, %).
           Los bloques de captura D1-D14 del cuestionario NO son unidades
           normativas: se conservan solo como "bloques internos de captura"
           con un semáforo porcentual referencial (no oficial).
Guía V  — Datos del trabajador. No genera resultado de riesgo (retorna None).

Reglas de integridad (ver docs/auditoria_metodologica_nom035.md):
- Ningún dato faltante se convierte en cero.
- Un cuestionario incompleto, fuera de rango o con filtros inconsistentes
  NO se clasifica: se marca `es_valido=False` / estatus "requiere_revision".
- Ítems 65-68 solo aplican si el trabajador atiende clientes (filtro D13);
  ítems 69-72 solo si supervisa trabajadores (filtro D14).
- El puntaje normativo es entero; no se redondea antes de clasificar.
- Todo resultado registra versión del motor y hash de las respuestas para
  reproducibilidad/auditoría.
"""

import hashlib
import json
from datetime import datetime, timezone as dt_timezone

# Versión del algoritmo. Incrementar ante CUALQUIER cambio de lógica o
# constantes para que los resultados persistidos sean trazables.
VERSION_MOTOR = '2.0.0'

ESCALA_MIN = 0
ESCALA_MAX = 4


def _categoria_por_rangos(puntaje, limites):
    """
    limites: lista de (max_exclusive, categoria) ordenada de menor a mayor.
    El último nivel (muy_alto) se retorna si se superan todos los límites.
    El límite inferior de cada nivel es inclusivo (lectura estándar de la
    notación del DOF: "50<Cfinal<75" == 50 ≤ Cfinal < 75).
    """
    for max_exclusive, categoria in limites:
        if puntaje < max_exclusive:
            return categoria
    return 'muy_alto'


# Alias público — clasificación con cortes oficiales.
clasificar = _categoria_por_rangos


# ---------------------------------------------------------------------------
# Guía III — cortes oficiales (GR.III, numeral III.3 inciso c)
# ---------------------------------------------------------------------------
_CORTES_FINAL = [(50, 'nulo'), (75, 'bajo'), (99, 'medio'), (140, 'alto')]  # Cfinal

_CORTES_CATEGORIA = {
    'Ambiente de trabajo':                  [(5, 'nulo'), (9, 'bajo'), (11, 'medio'), (14, 'alto')],
    'Factores propios de la actividad':     [(15, 'nulo'), (30, 'bajo'), (45, 'medio'), (60, 'alto')],
    'Organización del tiempo de trabajo':   [(5, 'nulo'), (7, 'bajo'), (10, 'medio'), (13, 'alto')],
    'Liderazgo y relaciones en el trabajo': [(14, 'nulo'), (29, 'bajo'), (42, 'medio'), (58, 'alto')],
    'Entorno organizacional':               [(10, 'nulo'), (14, 'bajo'), (18, 'medio'), (23, 'alto')],
}

_CORTES_DOMINIO = {
    'Condiciones en el ambiente de trabajo':               [(5, 'nulo'), (9, 'bajo'), (11, 'medio'), (14, 'alto')],
    'Carga de trabajo':                                    [(15, 'nulo'), (21, 'bajo'), (27, 'medio'), (37, 'alto')],
    'Falta de control sobre el trabajo':                   [(11, 'nulo'), (16, 'bajo'), (21, 'medio'), (25, 'alto')],
    'Jornada de trabajo':                                  [(1, 'nulo'), (2, 'bajo'), (4, 'medio'), (6, 'alto')],
    'Interferencia en la relación trabajo-familia':        [(4, 'nulo'), (6, 'bajo'), (8, 'medio'), (10, 'alto')],
    'Liderazgo':                                           [(9, 'nulo'), (12, 'bajo'), (16, 'medio'), (20, 'alto')],
    'Relaciones en el trabajo':                            [(10, 'nulo'), (13, 'bajo'), (17, 'medio'), (21, 'alto')],
    'Violencia':                                           [(7, 'nulo'), (10, 'bajo'), (13, 'medio'), (16, 'alto')],
    'Reconocimiento del desempeño':                        [(6, 'nulo'), (10, 'bajo'), (14, 'medio'), (18, 'alto')],
    'Insuficiente sentido de pertenencia e inestabilidad': [(4, 'nulo'), (6, 'bajo'), (8, 'medio'), (10, 'alto')],
}

# Aliases públicos (los informes/vistas deben consumir estos, nunca copiar
# los valores).
CORTES_FINAL    = _CORTES_FINAL
CORTES_CATEGORIA = _CORTES_CATEGORIA
CORTES_DOMINIO  = _CORTES_DOMINIO

# Estructura oficial: categoría (5) → dominios oficiales (10), en el orden de
# la Tabla 6.
_CATEGORIA_DOMINIOS = [
    ('Ambiente de trabajo', [
        'Condiciones en el ambiente de trabajo',
    ]),
    ('Factores propios de la actividad', [
        'Carga de trabajo',
        'Falta de control sobre el trabajo',
    ]),
    ('Organización del tiempo de trabajo', [
        'Jornada de trabajo',
        'Interferencia en la relación trabajo-familia',
    ]),
    ('Liderazgo y relaciones en el trabajo', [
        'Liderazgo',
        'Relaciones en el trabajo',
        'Violencia',
    ]),
    ('Entorno organizacional', [
        'Reconocimiento del desempeño',
        'Insuficiente sentido de pertenencia e inestabilidad',
    ]),
]

_CATEGORIAS_OFICIALES   = [c for c, _ in _CATEGORIA_DOMINIOS]
_DOMINIOS_OFICIALES     = [d for _, ds in _CATEGORIA_DOMINIOS for d in ds]
_DOMINIO_OFICIAL_CLAVE  = {nombre: f'D{i}' for i, nombre in enumerate(_DOMINIOS_OFICIALES, 1)}
_DOMINIO_OFICIAL_ORDEN  = {nombre: i for i, nombre in enumerate(_DOMINIOS_OFICIALES, 1)}
_CATEGORIA_DE_DOMINIO   = {dom: cat for cat, doms in _CATEGORIA_DOMINIOS for dom in doms}

CATEGORIAS_OFICIALES = _CATEGORIAS_OFICIALES
DOMINIOS_OFICIALES   = _DOMINIOS_OFICIALES

# Cortes porcentuales: SOLO indicador interno referencial para los 14 bloques
# de captura (D1-D14). La NOM-035 NO establece cortes por bloque; en informes
# estos bloques deben rotularse "Bloques internos de captura — análisis
# complementario no normativo".
_CUTOFFS_PCT = [(20, 'nulo'), (45, 'bajo'), (60, 'medio'), (75, 'alto')]

# ---------------------------------------------------------------------------
# Guía III — Tabla 5 (recodificación) y numeración oficial de ítems
# ---------------------------------------------------------------------------
# Offset de cada bloque de captura → número de ítem oficial (1-72).
_GUIA_III_ITEM_OFFSET = {
    'D1': 0,   'D2': 5,   'D3': 8,   'D4': 12,  'D5': 16,
    'D6': 22,  'D7': 28,  'D8': 30,  'D9': 36,  'D10': 41,
    'D11': 46, 'D12': 56, 'D13': 64, 'D14': 68,
}

# Tabla 5 oficial: ítems cuya calificación se invierte (Siempre=0 … Nunca=4).
# Verificada textualmente contra el DOF: 1, 4, 23-28, 30-53, 55, 56, 57.
# (El 29 y el 54 son directos.) El campo `Pregunta.inversa` de BD NO se usa
# para Guía III (contiene errores); la fuente de verdad es esta constante.
_GUIA_III_INVERSOS = frozenset(
    {1, 4}
    | set(range(23, 29))
    | {30}
    | set(range(31, 54))
    | {55, 56, 57}
)

# Ítems condicionados (GR.III): 65-68 solo si atiende clientes/usuarios
# (filtro del bloque D13); 69-72 solo si es jefe de otros trabajadores
# (filtro del bloque D14).
_ITEMS_SERVICIO_CLIENTES = frozenset({65, 66, 67, 68})
_ITEMS_JEFE              = frozenset({69, 70, 71, 72})
_ITEMS_CONDICIONADOS     = _ITEMS_SERVICIO_CLIENTES | _ITEMS_JEFE

# ---------------------------------------------------------------------------
# Guía III — Tabla 6: 25 dimensiones oficiales (transcritas del DOF).
# La NOM no define puntos de corte por dimensión: son SOLO descriptivas.
# ---------------------------------------------------------------------------
NOTA_DIMENSIONES = (
    'Indicador descriptivo. La NOM-035-STPS-2018 no establece puntos de '
    'corte por dimensión.'
)

_DIMENSIONES = [
    # (orden, dimensión, dominio oficial, ítems)
    (1,  'Condiciones peligrosas e inseguras',                    'Condiciones en el ambiente de trabajo',               (1, 3)),
    (2,  'Condiciones deficientes e insalubres',                  'Condiciones en el ambiente de trabajo',               (2, 4)),
    (3,  'Trabajos peligrosos',                                   'Condiciones en el ambiente de trabajo',               (5,)),
    (4,  'Cargas cuantitativas',                                  'Carga de trabajo',                                    (6, 12)),
    (5,  'Ritmos de trabajo acelerado',                           'Carga de trabajo',                                    (7, 8)),
    (6,  'Carga mental',                                          'Carga de trabajo',                                    (9, 10, 11)),
    (7,  'Cargas psicológicas emocionales',                       'Carga de trabajo',                                    (65, 66, 67, 68)),
    (8,  'Cargas de alta responsabilidad',                        'Carga de trabajo',                                    (13, 14)),
    (9,  'Cargas contradictorias o inconsistentes',               'Carga de trabajo',                                    (15, 16)),
    (10, 'Falta de control y autonomía sobre el trabajo',         'Falta de control sobre el trabajo',                   (25, 26, 27, 28)),
    (11, 'Limitada o nula posibilidad de desarrollo',             'Falta de control sobre el trabajo',                   (23, 24)),
    (12, 'Insuficiente participación y manejo del cambio',        'Falta de control sobre el trabajo',                   (29, 30)),
    (13, 'Limitada o inexistente capacitación',                   'Falta de control sobre el trabajo',                   (35, 36)),
    (14, 'Jornadas de trabajo extensas',                          'Jornada de trabajo',                                  (17, 18)),
    (15, 'Influencia del trabajo fuera del centro laboral',       'Interferencia en la relación trabajo-familia',        (19, 20)),
    (16, 'Influencia de las responsabilidades familiares',        'Interferencia en la relación trabajo-familia',        (21, 22)),
    (17, 'Escasa claridad de funciones',                          'Liderazgo',                                           (31, 32, 33, 34)),
    (18, 'Características del liderazgo',                         'Liderazgo',                                           (37, 38, 39, 40, 41)),
    (19, 'Relaciones sociales en el trabajo',                     'Relaciones en el trabajo',                            (42, 43, 44, 45, 46)),
    (20, 'Deficiente relación con los colaboradores que supervisa', 'Relaciones en el trabajo',                          (69, 70, 71, 72)),
    (21, 'Violencia laboral',                                     'Violencia',                                           (57, 58, 59, 60, 61, 62, 63, 64)),
    (22, 'Escasa o nula retroalimentación del desempeño',         'Reconocimiento del desempeño',                        (47, 48)),
    (23, 'Escaso o nulo reconocimiento y compensación',           'Reconocimiento del desempeño',                        (49, 50, 51, 52)),
    (24, 'Limitado sentido de pertenencia',                       'Insuficiente sentido de pertenencia e inestabilidad', (55, 56)),
    (25, 'Inestabilidad laboral',                                 'Insuficiente sentido de pertenencia e inestabilidad', (53, 54)),
]

DIMENSIONES = _DIMENSIONES


def _item_guia_iii(dcl, orden):
    return _GUIA_III_ITEM_OFFSET[dcl] + orden


# Mapeo bloque de captura (D1-D14) → dominio oficial (Tabla 6).
_MAPA_DOMINIO = {
    'D1':  'Condiciones en el ambiente de trabajo',
    'D2':  'Carga de trabajo',
    'D3':  'Carga de trabajo',
    'D4':  'Carga de trabajo',
    'D6':  'Falta de control sobre el trabajo',
    'D7':  'Falta de control sobre el trabajo',
    'D9':  'Liderazgo',
    'D10': 'Relaciones en el trabajo',
    'D12': 'Violencia',
    'D13': 'Carga de trabajo',
    'D14': 'Relaciones en el trabajo',
}


def _dominio_oficial(dcl, orden):
    if dcl == 'D5':
        return 'Jornada de trabajo' if orden <= 2 else 'Interferencia en la relación trabajo-familia'
    if dcl == 'D8':
        return 'Liderazgo' if orden <= 4 else 'Falta de control sobre el trabajo'
    if dcl == 'D11':
        return 'Reconocimiento del desempeño' if orden <= 6 else 'Insuficiente sentido de pertenencia e inestabilidad'
    return _MAPA_DOMINIO[dcl]


def puntaje_item_guia_iii(item, valor):
    """Recodificación oficial (Tabla 5) por número de ítem 1-72. `valor` es
    la respuesta cruda almacenada (Nunca=0 … Siempre=4). No acepta faltantes:
    la validación debe ejecutarse antes."""
    return (ESCALA_MAX - valor) if item in _GUIA_III_INVERSOS else valor


def _ahora_iso():
    return datetime.now(dt_timezone.utc).isoformat()


def hash_respuestas(respuestas):
    """SHA-256 estable del conjunto de respuestas (para reproducibilidad).
    `respuestas`: dict {pregunta_id: RespuestaPregunta}."""
    canon = sorted(
        (int(pid), r.valor if r.valor is not None else None,
         (r.valor_texto or '') if getattr(r, 'valor_texto', None) is not None else '')
        for pid, r in respuestas.items()
    )
    blob = json.dumps(canon, ensure_ascii=False, separators=(',', ':'))
    return hashlib.sha256(blob.encode('utf-8')).hexdigest()


def _nueva_validacion():
    return {
        'es_valido': True,
        'errores_criticos': [],
        'advertencias': [],
        'reactivos_faltantes': [],
        'reactivos_fuera_de_rango': [],
        'inconsistencias_filtros': [],
        'fecha_validacion': _ahora_iso(),
        'version_motor': VERSION_MOTOR,
    }


def _invalidar(validacion, mensaje):
    validacion['es_valido'] = False
    if mensaje not in validacion['errores_criticos']:
        validacion['errores_criticos'].append(mensaje)


# ---------------------------------------------------------------------------
# Guía I — Acontecimientos Traumáticos Severos
# ---------------------------------------------------------------------------

# Criterios GR.I inciso b: número mínimo de "Sí" con el que cada sección se
# considera positiva. La Sección I (D1) es el filtro de entrada: basta un "Sí"
# para que se haya reportado un acontecimiento traumático severo.
CRITERIOS_GUIA_I = {'D1': 1, 'D2': 1, 'D3': 3, 'D4': 2}


def _calcular_guia_i(aplicacion, respuestas):
    """GR.I incisos a y b. Un "Sí" faltante NUNCA se cuenta como "No": si la
    Sección I está incompleta —o si hubo acontecimiento y las secciones
    II-IV están incompletas— el cuestionario queda en revisión sin
    resultado clínico."""
    validacion = _nueva_validacion()

    dominios_result = []
    puntaje_total = 0
    puntaje_max_total = 0
    conteo = {}          # {clave_bloque: nº de "Sí"}
    faltantes = {}       # {clave_bloque: [pregunta_id, ...]}

    for dominio in aplicacion.cuestionario.dominios.prefetch_related('preguntas').all():
        preguntas = list(dominio.preguntas.all())
        positivos = 0
        for p in preguntas:
            r = respuestas.get(p.id)
            if r is None or r.valor is None:
                faltantes.setdefault(dominio.clave, []).append(p.id)
                continue
            if r.valor not in (0, 1):
                validacion['reactivos_fuera_de_rango'].append(
                    {'pregunta_id': p.id, 'seccion': dominio.clave, 'valor': r.valor})
                continue
            positivos += 1 if r.valor == 1 else 0

        conteo[dominio.clave] = positivos
        puntaje_total     += positivos
        puntaje_max_total += len(preguntas)
        dominios_result.append({
            'dominio_id':     dominio.id,
            'dominio_clave':  dominio.clave,
            'dominio_nombre': dominio.nombre,
            'puntaje':        positivos,
            'puntaje_max':    len(preguntas),
            'categoria':      'alto' if (dominio.clave != 'D1' and positivos > 0) else 'nulo',
        })

    seccion_i   = conteo.get('D1', 0)
    seccion_ii  = conteo.get('D2', 0)
    seccion_iii = conteo.get('D3', 0)
    seccion_iv  = conteo.get('D4', 0)

    # Reglas de completitud (GR.I inciso a): la Sección I es siempre
    # obligatoria; si toda la Sección I es "No", las secciones II-IV pueden
    # omitirse; si hay algún "Sí", las secciones II-IV son obligatorias.
    if faltantes.get('D1'):
        validacion['reactivos_faltantes'].extend(faltantes['D1'])
        _invalidar(validacion, 'Sección I incompleta: no se puede determinar si hubo acontecimiento.')
    elif seccion_i >= 1:
        for clave in ('D2', 'D3', 'D4'):
            if faltantes.get(clave):
                validacion['reactivos_faltantes'].extend(faltantes[clave])
        if validacion['reactivos_faltantes']:
            _invalidar(validacion,
                       'Hubo acontecimiento (Sección I) y las secciones II-IV están incompletas.')
    if validacion['reactivos_fuera_de_rango']:
        _invalidar(validacion, 'Respuestas fuera del rango Sí/No.')

    reporta_ats = seccion_i   >= CRITERIOS_GUIA_I['D1']
    cumple_ii   = seccion_ii  >= CRITERIOS_GUIA_I['D2']
    cumple_iii  = seccion_iii >= CRITERIOS_GUIA_I['D3']
    cumple_iv   = seccion_iv  >= CRITERIOS_GUIA_I['D4']
    requiere_atencion = bool(reporta_ats and (cumple_ii or cumple_iii or cumple_iv))

    if not validacion['es_valido']:
        return {
            'es_valido':         False,
            'validacion':        validacion,
            'puntaje_total':     puntaje_total,
            'puntaje_max':       puntaje_max_total,
            'categoria':         None,
            'requiere_atencion': None,
            'dominios':          dominios_result,
            'guia_i':            None,
        }

    return {
        'es_valido':         True,
        'validacion':        validacion,
        'puntaje_total':     puntaje_total,
        'puntaje_max':       puntaje_max_total,
        'categoria':         'requiere_atencion' if requiere_atencion else 'sin_indicadores',
        'requiere_atencion': requiere_atencion,
        'dominios':          dominios_result,
        'guia_i': {
            'reporta_ats':               reporta_ats,
            'seccion_i':                 seccion_i,
            'seccion_ii':                seccion_ii,
            'seccion_iii':               seccion_iii,
            'seccion_iv':                seccion_iv,
            'cumple_criterio_ii':        cumple_ii,
            'cumple_criterio_iii':       cumple_iii,
            'cumple_criterio_iv':        cumple_iv,
            'requiere_atencion_clinica': requiere_atencion,
            'estatus_validacion':        'valido',
        },
    }


# ---------------------------------------------------------------------------
# Guía III — mapeo, validación y calificación
# ---------------------------------------------------------------------------

def _mapear_guia_iii(aplicacion):
    """Estructura del cuestionario: lista de bloques
    (dominio, pregunta_filtro | None, [(item_oficial, pregunta), ...])."""
    bloques = []
    for dominio in aplicacion.cuestionario.dominios.prefetch_related('preguntas').all():
        filtro = None
        items = []
        for pregunta in dominio.preguntas.all():
            if pregunta.tipo_respuesta == 'si_no':
                filtro = pregunta
            elif pregunta.tipo_respuesta == 'frecuencia':
                items.append((_item_guia_iii(dominio.clave, pregunta.orden), pregunta))
        bloques.append((dominio, filtro, items))
    return bloques


def _validar_guia_iii(bloques, respuestas):
    """Aplica las reglas de completitud/consistencia. Regresa
    (validacion, filtros, items_aplicables) donde `filtros` es
    {clave_bloque: True/False/None} y `items_aplicables` el set de números de
    ítem que participan en las sumas."""
    validacion = _nueva_validacion()
    filtros = {}
    items_aplicables = set()

    preguntas_reconocidas = set()

    for dominio, filtro, items in bloques:
        aplica = True
        if filtro is not None:
            preguntas_reconocidas.add(filtro.id)
            r = respuestas.get(filtro.id)
            if r is None or r.valor is None:
                filtros[dominio.clave] = None
                validacion['reactivos_faltantes'].append(
                    {'pregunta_id': filtro.id, 'bloque': dominio.clave, 'tipo': 'filtro'})
                _invalidar(validacion,
                           f'Filtro del bloque {dominio.clave} sin responder: cuestionario incompleto.')
                aplica = None
            elif r.valor not in (0, 1):
                filtros[dominio.clave] = None
                validacion['reactivos_fuera_de_rango'].append(
                    {'pregunta_id': filtro.id, 'bloque': dominio.clave, 'valor': r.valor, 'tipo': 'filtro'})
                _invalidar(validacion, f'Filtro del bloque {dominio.clave} con valor inválido.')
                aplica = None
            else:
                aplica = bool(r.valor == 1)
                filtros[dominio.clave] = aplica

        for item, pregunta in items:
            preguntas_reconocidas.add(pregunta.id)
            r = respuestas.get(pregunta.id)
            contestado = r is not None and r.valor is not None

            if aplica is True:
                if not contestado:
                    validacion['reactivos_faltantes'].append(
                        {'pregunta_id': pregunta.id, 'item': item, 'bloque': dominio.clave})
                elif not (ESCALA_MIN <= r.valor <= ESCALA_MAX):
                    validacion['reactivos_fuera_de_rango'].append(
                        {'pregunta_id': pregunta.id, 'item': item, 'valor': r.valor})
                else:
                    items_aplicables.add(item)
            elif aplica is False:
                # Filtro "No": los condicionados no aplican; si fueron
                # contestados es una inconsistencia que se registra (no se
                # suman, no invalida por sí sola).
                if contestado:
                    validacion['inconsistencias_filtros'].append({
                        'pregunta_id': pregunta.id, 'item': item, 'bloque': dominio.clave,
                        'detalle': 'Reactivo condicionado contestado con filtro "No".',
                    })
            # aplica is None (filtro faltante/ inválido): ya se invalidó.

    if validacion['reactivos_faltantes'] and validacion['es_valido']:
        _invalidar(validacion, 'Reactivos obligatorios sin respuesta.')
    if validacion['reactivos_fuera_de_rango'] and validacion['es_valido']:
        _invalidar(validacion, 'Respuestas fuera del rango permitido (0-4).')
    if validacion['inconsistencias_filtros']:
        validacion['advertencias'].append(
            'Reactivos condicionados contestados aunque el filtro fue "No"; '
            'se excluyeron de la calificación y requieren revisión.')

    no_reconocidas = set(respuestas) - preguntas_reconocidas
    if no_reconocidas:
        validacion['advertencias'].append(
            f'{len(no_reconocidas)} respuesta(s) a preguntas que no pertenecen al cuestionario; se ignoraron.')

    return validacion, filtros, items_aplicables


def _calcular_guia_iii(aplicacion, respuestas):
    bloques = _mapear_guia_iii(aplicacion)
    validacion, filtros, items_aplicables = _validar_guia_iii(bloques, respuestas)

    if not validacion['es_valido']:
        return {
            'es_valido':          False,
            'validacion':         validacion,
            'puntaje_total':      None,
            'puntaje_max':        None,
            'categoria':          None,
            'requiere_atencion':  None,
            'dominios':           [],
            'dominios_oficiales': [],
            'categorias':         [],
            'dimensiones':        [],
        }

    # ---- puntaje recodificado por ítem oficial (solo ítems aplicables) ----
    puntaje_por_item = {}
    for dominio, _filtro, items in bloques:
        for item, pregunta in items:
            if item in items_aplicables:
                puntaje_por_item[item] = puntaje_item_guia_iii(item, respuestas[pregunta.id].valor)

    # ---- bloques internos de captura (D1-D14, NO normativos) ----
    dominios_result = []
    for dominio, _filtro, items in bloques:
        aplicables = [(i, p) for i, p in items if i in items_aplicables]
        puntaje     = sum(puntaje_por_item[i] for i, _ in aplicables)
        puntaje_max = ESCALA_MAX * len(aplicables)
        dominios_result.append({
            'dominio_id':     dominio.id,
            'dominio_clave':  dominio.clave,
            'dominio_nombre': dominio.nombre,
            'puntaje':        puntaje,
            'puntaje_max':    puntaje_max,
            # Semáforo porcentual REFERENCIAL (no oficial): ver _CUTOFFS_PCT.
            'categoria':      _categoria_por_rangos(
                round(puntaje / puntaje_max * 100) if puntaje_max else 0,
                _CUTOFFS_PCT,
            ),
        })

    # ---- 10 dominios oficiales (Tabla 6) ----
    oficiales = {nombre: {'puntaje': 0, 'puntaje_max': 0} for nombre in _DOMINIOS_OFICIALES}
    for dominio, _filtro, items in bloques:
        for item, _pregunta in items:
            if item not in items_aplicables:
                continue
            nombre = _dominio_oficial(dominio.clave, _pregunta_orden(item, dominio.clave))
            oficiales[nombre]['puntaje']     += puntaje_por_item[item]
            oficiales[nombre]['puntaje_max'] += ESCALA_MAX

    dominios_oficiales_result = [
        {
            'clave':       _DOMINIO_OFICIAL_CLAVE[nombre],
            'nombre':      nombre,
            'orden':       _DOMINIO_OFICIAL_ORDEN[nombre],
            'puntaje':     oficiales[nombre]['puntaje'],
            'puntaje_max': oficiales[nombre]['puntaje_max'],
            'categoria':   _categoria_por_rangos(oficiales[nombre]['puntaje'], _CORTES_DOMINIO[nombre]),
        }
        for nombre in _DOMINIOS_OFICIALES
    ]

    # ---- 5 categorías oficiales (suma de sus dominios, Tabla 6) ----
    categorias_result = []
    for orden_cat, (cat, doms) in enumerate(_CATEGORIA_DOMINIOS, 1):
        pt = sum(oficiales[d]['puntaje'] for d in doms)
        pm = sum(oficiales[d]['puntaje_max'] for d in doms)
        categorias_result.append({
            'nombre':      cat,
            'orden':       orden_cat,
            'puntaje':     pt,
            'puntaje_max': pm,
            'categoria':   _categoria_por_rangos(pt, _CORTES_CATEGORIA[cat]),
        })

    # ---- 25 dimensiones oficiales — SOLO descriptivas (sin niveles) ----
    dimensiones_result = []
    for orden_dim, nombre, dom_oficial, items_dim in _DIMENSIONES:
        aplicables = [i for i in items_dim if i in items_aplicables]
        pt = sum(puntaje_por_item[i] for i in aplicables)
        pm = ESCALA_MAX * len(aplicables)
        dimensiones_result.append({
            'orden':            orden_dim,
            'nombre':           nombre,
            'dominio_oficial':  dom_oficial,
            'categoria_oficial': _CATEGORIA_DE_DOMINIO[dom_oficial],
            'items':            list(items_dim),
            'items_aplicables': aplicables,
            'puntaje':          pt,
            'puntaje_max':      pm,
            'pct':              round(pt / pm * 100, 1) if pm else None,
            'nota':             NOTA_DIMENSIONES,
        })

    # ---- Calificación final (Cfinal) ----
    puntaje_total = sum(puntaje_por_item.values())
    puntaje_max   = ESCALA_MAX * len(items_aplicables)

    return {
        'es_valido':          True,
        'validacion':         validacion,
        'filtros':            filtros,
        'puntaje_total':      puntaje_total,
        'puntaje_max':        puntaje_max,
        'categoria':          _categoria_por_rangos(puntaje_total, _CORTES_FINAL),
        'requiere_atencion':  None,
        'dominios':           dominios_result,
        'dominios_oficiales': dominios_oficiales_result,
        'categorias':         categorias_result,
        'dimensiones':        dimensiones_result,
    }


def _pregunta_orden(item, dominio_clave):
    """Orden de la pregunta dentro de su bloque a partir del ítem oficial."""
    return item - _GUIA_III_ITEM_OFFSET[dominio_clave]


# ---------------------------------------------------------------------------
# Punto de entrada público
# ---------------------------------------------------------------------------

def validar_aplicacion(aplicacion) -> dict | None:
    """Solo la validación estructurada (sin calificar). None para Guía V."""
    resultado = calcular_resultado(aplicacion)
    return resultado['validacion'] if resultado else None


def calcular_resultado(aplicacion) -> dict | None:
    """
    Calcula el resultado normativo de una `Aplicacion`.

    Retorna None para Guía V (no genera resultado de riesgo). Para las
    guías I y III retorna un dict con:
      es_valido, validacion, version_motor, hash_respuestas,
      puntaje_total, puntaje_max, categoria, requiere_atencion, dominios
    y, para Guía III: dominios_oficiales, categorias (5 oficiales) y
    dimensiones (25, descriptivas). Si `es_valido` es False el cuestionario
    NO se clasifica (categoria=None) y debe quedar en "requiere_revision".

    Función pura respecto de BD: no escribe nada; la persistencia (con
    transacción e idempotencia) es responsabilidad de la vista/servicio.
    """
    respuestas = {r.pregunta_id: r for r in aplicacion.respuestas.all()}
    guia       = aplicacion.cuestionario.clave

    if guia == 'V':
        return None
    if guia == 'I':
        resultado = _calcular_guia_i(aplicacion, respuestas)
    elif guia == 'III':
        resultado = _calcular_guia_iii(aplicacion, respuestas)
    else:
        return None

    resultado['version_motor']   = VERSION_MOTOR
    resultado['hash_respuestas'] = hash_respuestas(respuestas)
    return resultado
