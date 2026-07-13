"""
Motor de calificación NOM-035-STPS-2018.

Guía I  — Acontecimiento Traumático Severo (ATS). Resultado binario:
          requiere_atencion = True si D1 (Sección I) ≥ 1 positivo Y al menos
          uno de: Sección II (D2) ≥ 1, Sección III (D3) ≥ 3, Sección IV
          (D4) ≥ 2 — apartado GR.I inciso b). No es una suma combinada de
          D2+D3+D4: cada sección tiene su propio umbral independiente.
Guía III — Factores de riesgo psicosocial. El cuestionario está organizado en
           14 bloques (D1-D14) por conveniencia de captura, pero la Guía de
           Referencia III califica sobre 10 dominios oficiales y una
           calificación global (Tabla 6, Cuadro de puntajes). Este módulo
           calcula ambos niveles:
           - `dominios`: los 14 bloques crudos, con un indicador de nivel
             solo referencial (la NOM-035 no define cortes por bloque).
           - `dominios_oficiales`: los 10 dominios oficiales, reagrupando
             ítems de varios bloques según la Tabla 6, con los cortes
             oficiales de suma.
           D13/D14 son opcionales: solo se califican si el trabajador respondió
           "Sí" a la pregunta filtro de cada dominio.
Guía V  — Datos del trabajador. No genera resultado de riesgo (retorna None).

Fuente de la metodología: Guía de Referencia III, NOM-035-STPS-2018 (DOF
23-oct-2018), validada contra los datos reales del cliente el 2026-07-07
(ver `generar_informe.py` en la raíz del repo, de donde se portó esta lógica).
"""


def _categoria_por_rangos(puntaje, limites):
    """
    limites: lista de (max_exclusive, categoria) ordenada de menor a mayor.
    El último nivel (muy_alto) se retorna si se superan todos los límites.
    """
    for max_exclusive, categoria in limites:
        if puntaje < max_exclusive:
            return categoria
    return 'muy_alto'


# ---------------------------------------------------------------------------
# Guía III — calificación oficial (Tabla 6, Guía de Referencia III)
# La calificación se obtiene SUMANDO ítems (Cfinal, Ccat, Cdom), sin
# porcentajes. Cada lista contiene (límite superior exclusivo, nivel); arriba
# del último nivel listado se asigna 'muy_alto'.
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

# Estructura oficial: categoría (5) → dominios oficiales (10), en el orden de
# la Tabla 6. `_DOMINIOS_OFICIALES` es la lista plana en ese mismo orden y
# `_DOMINIO_OFICIAL_CLAVE` asigna una clave corta y estable por posición
# ('D1'..'D10'), usada como identificador en `ResultadoDominioOficial` y en
# el frontend (heatmap, gráfica de barras, top-3).
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

_DOMINIOS_OFICIALES     = [d for _, ds in _CATEGORIA_DOMINIOS for d in ds]
_DOMINIO_OFICIAL_CLAVE  = {nombre: f'D{i}' for i, nombre in enumerate(_DOMINIOS_OFICIALES, 1)}
_DOMINIO_OFICIAL_ORDEN  = {nombre: i for i, nombre in enumerate(_DOMINIOS_OFICIALES, 1)}

# Cortes porcentuales: SOLO indicador interno referencial para los 14 bloques
# crudos del cuestionario (D1-D14). La NOM-035 no establece puntos de corte
# por bloque — el nivel oficial de riesgo se determina por dominio (10) y de
# forma global, no por bloque.
_CUTOFFS_PCT = [(20, 'nulo'), (45, 'bajo'), (60, 'medio'), (75, 'alto')]

# Tabla 5, Guía III: codificación oficial de inversión por número de ítem
# (1-72). El campo `Pregunta.inversa` en BD no es confiable para Guía III
# (3 ítems están mal marcados), así que la inversión se calcula desde esta
# tabla fija, igual que en `generar_informe.py`.
_GUIA_III_ITEM_OFFSET = {
    'D1': 0,   'D2': 5,   'D3': 8,   'D4': 12,  'D5': 16,
    'D6': 22,  'D7': 28,  'D8': 30,  'D9': 36,  'D10': 41,
    'D11': 46, 'D12': 56, 'D13': 64, 'D14': 68,
}
_GUIA_III_INVERSOS = (
    {1, 4}
    | set(range(23, 29))
    | {30}
    | set(range(31, 54))
    | {55, 56, 57}
)


def _item_guia_iii(dcl, orden):
    return _GUIA_III_ITEM_OFFSET[dcl] + orden


# Mapeo bloque del cuestionario (D1-D14) → dominio oficial de la Guía III.
# Los bloques D5, D8 y D11 se dividen por número de pregunta porque agrupan
# ítems de dominios oficiales distintos (ver `_dominio_oficial`); D13 (cargas
# emocionales) suma a Carga de trabajo y D14 (colaboradores que supervisa) a
# Relaciones en el trabajo, conforme a la Tabla 6.
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


def _valor_item_guia_iii(dominio_clave, pregunta_orden, respuesta):
    """Puntaje ponderado de una respuesta de Guía III: invierte la escala si
    el ítem (por número oficial, no por `Pregunta.inversa`) es inverso."""
    if not respuesta or respuesta.valor is None:
        return 0
    item = _item_guia_iii(dominio_clave, pregunta_orden)
    return (4 - respuesta.valor) if item in _GUIA_III_INVERSOS else respuesta.valor


# ---------------------------------------------------------------------------
# Guía I
# ---------------------------------------------------------------------------

def _calcular_guia_i(aplicacion, respuestas):
    dominios_result = []
    puntaje_total   = 0
    puntaje_max_total = 0
    hay_acontecimiento = False  # D1 (Sección I) tiene al menos 1 "Sí"
    puntaje_por_seccion = {}    # D2/D3/D4 = Secciones II/III/IV, por separado

    for dominio in aplicacion.cuestionario.dominios.prefetch_related('preguntas').all():
        preguntas = list(dominio.preguntas.all())
        puntaje   = sum(
            1 for p in preguntas
            if respuestas.get(p.id) and respuestas[p.id].valor == 1
        )

        if dominio.clave == 'D1':
            hay_acontecimiento = puntaje >= 1
        else:
            # D2 = Sección II, D3 = Sección III, D4 = Sección IV
            puntaje_por_seccion[dominio.clave] = puntaje

        puntaje_total     += puntaje
        puntaje_max_total += len(preguntas)

        dominios_result.append({
            'dominio_id':     dominio.id,
            'dominio_clave':  dominio.clave,
            'dominio_nombre': dominio.nombre,
            'puntaje':        puntaje,
            'puntaje_max':    len(preguntas),
            'categoria':      'alto' if (dominio.clave != 'D1' and puntaje > 0) else 'nulo',
        })

    # Criterio NOM-035 (Guía I, apartado GR.I inciso b): D1 (Sección I) ≥ 1
    # positivo Y al menos uno de: Sección II (D2) ≥ 1, Sección III (D3) ≥ 3,
    # o Sección IV (D4) ≥ 2. NO es una suma combinada de D2+D3+D4 — cada
    # sección tiene su propio umbral independiente (ver generar_informe.py,
    # validado con el cliente).
    requiere_atencion = hay_acontecimiento and (
        puntaje_por_seccion.get('D2', 0) >= 1
        or puntaje_por_seccion.get('D3', 0) >= 3
        or puntaje_por_seccion.get('D4', 0) >= 2
    )

    return {
        'puntaje_total':     puntaje_total,
        'puntaje_max':       puntaje_max_total,
        'categoria':         'requiere_atencion' if requiere_atencion else 'sin_indicadores',
        'requiere_atencion': requiere_atencion,
        'dominios':          dominios_result,
    }


# ---------------------------------------------------------------------------
# Guía III
# ---------------------------------------------------------------------------

def _es_dominio_condicional(dominio):
    """D13 y D14 tienen una pregunta si_no que actúa como filtro."""
    return any(p.tipo_respuesta == 'si_no' for p in dominio.preguntas.all())


def _filtro_contestado_si(dominio, respuestas):
    """Retorna True si la pregunta filtro (si_no) del dominio fue respondida con Sí (valor=1)."""
    for pregunta in dominio.preguntas.all():
        if pregunta.tipo_respuesta == 'si_no':
            r = respuestas.get(pregunta.id)
            return bool(r and r.valor == 1)
    return False


def _calcular_guia_iii(aplicacion, respuestas):
    dominios_result   = []
    puntaje_total     = 0
    puntaje_max_total = 0
    oficiales = {nombre: {'puntaje': 0, 'puntaje_max': 0} for nombre in _DOMINIOS_OFICIALES}

    for dominio in aplicacion.cuestionario.dominios.prefetch_related('preguntas').all():
        # D13/D14: verificar si el trabajador respondió "Sí" al filtro
        es_condicional = _es_dominio_condicional(dominio)
        if es_condicional and not _filtro_contestado_si(dominio, respuestas):
            # El trabajador no aplica a este dominio — incluir con 0/0 sin sumar al total
            dominios_result.append({
                'dominio_id':     dominio.id,
                'dominio_clave':  dominio.clave,
                'dominio_nombre': dominio.nombre,
                'puntaje':        0,
                'puntaje_max':    0,
                'categoria':      'nulo',
            })
            continue

        puntaje     = 0
        puntaje_max = 0
        for pregunta in dominio.preguntas.all():
            if pregunta.tipo_respuesta != 'frecuencia':
                continue
            valor = _valor_item_guia_iii(dominio.clave, pregunta.orden, respuestas.get(pregunta.id))
            puntaje     += valor
            puntaje_max += 4

            dom_oficial = _dominio_oficial(dominio.clave, pregunta.orden)
            oficiales[dom_oficial]['puntaje']     += valor
            oficiales[dom_oficial]['puntaje_max'] += 4

        dominios_result.append({
            'dominio_id':     dominio.id,
            'dominio_clave':  dominio.clave,
            'dominio_nombre': dominio.nombre,
            'puntaje':        puntaje,
            'puntaje_max':    puntaje_max,
            'categoria':      _categoria_por_rangos(
                round(puntaje / puntaje_max * 100) if puntaje_max else 0,
                _CUTOFFS_PCT,
            ),
        })
        puntaje_total     += puntaje
        puntaje_max_total += puntaje_max

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

    return {
        'puntaje_total':      puntaje_total,
        'puntaje_max':        puntaje_max_total,
        'categoria':          _categoria_por_rangos(puntaje_total, _CORTES_FINAL),
        'requiere_atencion':  None,
        'dominios':           dominios_result,
        'dominios_oficiales': dominios_oficiales_result,
    }


# ---------------------------------------------------------------------------
# Punto de entrada público
# ---------------------------------------------------------------------------

def calcular_resultado(aplicacion) -> dict | None:
    """
    Retorna dict con puntaje_total, puntaje_max, categoria, requiere_atencion, dominios.
    Guía III incluye además `dominios_oficiales` (10 dominios, Tabla 6).
    Retorna None para Guía V (no genera resultado de riesgo).
    """
    respuestas = {r.pregunta_id: r for r in aplicacion.respuestas.all()}
    guia       = aplicacion.cuestionario.clave

    if guia == 'V':
        return None
    if guia == 'I':
        return _calcular_guia_i(aplicacion, respuestas)
    if guia == 'III':
        return _calcular_guia_iii(aplicacion, respuestas)

    return None
