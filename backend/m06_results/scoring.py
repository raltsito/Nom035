"""
Motor de calificación NOM-035-STPS-2018.

Guía I  — Acontecimiento Traumático Severo (ATS). Resultado binario:
          requiere_atencion = True si D1 ≥ 1 positivo Y (D2+D3+D4) ≥ 2 positivos.
Guía III — Factores de riesgo psicosocial. 14 dominios, escala de frecuencia 0-4.
           D13/D14 son opcionales: solo se califican si el trabajador respondió
           "Sí" a la pregunta filtro de cada dominio.
Guía V  — Datos del trabajador. No genera resultado de riesgo (retorna None).

Rangos basados en la Guía de Referencia III y metodología oficial NOM-035-STPS-2018
(DOF 23-oct-2018). Verificar contra tabla oficial antes de publicar en producción.
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
# Guía III — rangos globales
# Fuente: Cuadro de puntajes Guía de Referencia III, NOM-035-STPS-2018
# ---------------------------------------------------------------------------
GUIA_III_GLOBAL = [
    (20,  'nulo'),
    (45,  'bajo'),
    (80,  'medio'),
    (141, 'alto'),
]

# ---------------------------------------------------------------------------
# Guía III — rangos por dominio
# Cada entrada: (max_exclusive, categoria). Último nivel implícito = muy_alto.
# ---------------------------------------------------------------------------
GUIA_III_DOMINIOS = {
    # D1  Condiciones en el ambiente de trabajo — P1-P5   (máx 20)
    'D1':  [(3,  'nulo'), (6,  'bajo'), (12, 'medio'), (17, 'alto')],
    # D2  Ritmo de trabajo — P6-P8                        (máx 12)
    'D2':  [(1,  'nulo'), (3,  'bajo'), (6,  'medio'), (9,  'alto')],
    # D3  Esfuerzo mental — P9-P12                        (máx 16)
    'D3':  [(4,  'nulo'), (7,  'bajo'), (10, 'medio'), (13, 'alto')],
    # D4  Actividades y responsabilidades — P13-P16        (máx 16)
    'D4':  [(2,  'nulo'), (4,  'bajo'), (8,  'medio'), (13, 'alto')],
    # D5  Jornada de trabajo — P17-P22                    (máx 24)
    'D5':  [(3,  'nulo'), (7,  'bajo'), (12, 'medio'), (20, 'alto')],
    # D6  Decisiones en el trabajo (inv.) — P23-P28       (máx 24)
    'D6':  [(4,  'nulo'), (9,  'bajo'), (14, 'medio'), (19, 'alto')],
    # D7  Cambios en el trabajo (inv.) — P29-P30          (máx 8)
    'D7':  [(1,  'nulo'), (3,  'bajo'), (5,  'medio'), (7,  'alto')],
    # D8  Capacitación (inv.) — P31-P36                   (máx 24)
    'D8':  [(4,  'nulo'), (9,  'bajo'), (14, 'medio'), (18, 'alto')],
    # D9  Liderazgo / Subordinación (inv.) — P37-P41      (máx 20)
    'D9':  [(3,  'nulo'), (6,  'bajo'), (10, 'medio'), (15, 'alto')],
    # D10 Relaciones con compañeros (inv.) — P42-P46      (máx 20)
    'D10': [(3,  'nulo'), (6,  'bajo'), (10, 'medio'), (15, 'alto')],
    # D11 Rendimiento y reconocimiento (mix.) — P47-P56   (máx 40)
    'D11': [(6,  'nulo'), (13, 'bajo'), (21, 'medio'), (31, 'alto')],
    # D12 Violencia laboral (mix.) — P57-P64              (máx 32)
    'D12': [(1,  'nulo'), (4,  'bajo'), (7,  'medio'), (13, 'alto')],
    # D13 Atención a clientes* — P65-P68                  (máx 16)
    'D13': [(1,  'nulo'), (3,  'bajo'), (6,  'medio'), (11, 'alto')],
    # D14 Actitudes de supervisados* — P69-P72            (máx 16)
    'D14': [(1,  'nulo'), (3,  'bajo'), (6,  'medio'), (11, 'alto')],
}


def _valor_puntaje(respuesta, pregunta):
    """Puntaje ponderado de una respuesta: invierte la escala si la pregunta es inversa."""
    if not respuesta or respuesta.valor is None:
        return 0
    return (4 - respuesta.valor) if pregunta.inversa else respuesta.valor


# ---------------------------------------------------------------------------
# Guía I
# ---------------------------------------------------------------------------

def _calcular_guia_i(aplicacion, respuestas):
    dominios_result = []
    puntaje_total   = 0
    puntaje_max_total = 0
    hay_acontecimiento = False  # D1 tiene al menos 1 "Sí"
    sintomas_total     = 0      # total de "Sí" en D2 + D3 + D4

    for dominio in aplicacion.cuestionario.dominios.prefetch_related('preguntas').all():
        preguntas = list(dominio.preguntas.all())
        puntaje   = sum(
            1 for p in preguntas
            if respuestas.get(p.id) and respuestas[p.id].valor == 1
        )

        if dominio.clave == 'D1':
            hay_acontecimiento = puntaje >= 1
        else:
            # D2, D3, D4 — secciones de síntomas
            sintomas_total += puntaje

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

    # Criterio NOM-035: D1 ≥ 1 positivo  Y  (D2+D3+D4) ≥ 2 positivos
    requiere_atencion = hay_acontecimiento and sintomas_total >= 2

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
    dominios_result  = []
    puntaje_total    = 0
    puntaje_max_total = 0

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
            puntaje_max += 4
            puntaje     += _valor_puntaje(respuestas.get(pregunta.id), pregunta)

        dominios_result.append({
            'dominio_id':     dominio.id,
            'dominio_clave':  dominio.clave,
            'dominio_nombre': dominio.nombre,
            'puntaje':        puntaje,
            'puntaje_max':    puntaje_max,
            'categoria':      _categoria_por_rangos(
                puntaje,
                GUIA_III_DOMINIOS.get(dominio.clave, [(9999, 'nulo')]),
            ),
        })
        puntaje_total     += puntaje
        puntaje_max_total += puntaje_max

    return {
        'puntaje_total':     puntaje_total,
        'puntaje_max':       puntaje_max_total,
        'categoria':         _categoria_por_rangos(puntaje_total, GUIA_III_GLOBAL),
        'requiere_atencion': None,
        'dominios':          dominios_result,
    }


# ---------------------------------------------------------------------------
# Punto de entrada público
# ---------------------------------------------------------------------------

def calcular_resultado(aplicacion) -> dict | None:
    """
    Retorna dict con puntaje_total, puntaje_max, categoria, requiere_atencion, dominios.
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
