"""
Motor de calificacion NOM-035-STPS-2018.
Umbrales oficiales de riesgo por guia y dominio.
Formato: [(puntaje_max_inclusive, categoria), ...]  — primer match gana.
"""

# ---------------------------------------------------------------------------
# Tablas de umbrales por Guia y Dominio
# ---------------------------------------------------------------------------

THRESHOLDS: dict[str, dict[str, list]] = {

    # ---- Guia I (<=15 trabajadores, 23 preguntas) ----
    'I': {
        'global': [(8, 'bajo'), (14, 'medio'), (24, 'alto'), (9999, 'muy_alto')],
        'D1':     [(2, 'bajo'), (4,  'medio'), (7,  'alto'), (9999, 'muy_alto')],
        'D2':     [(1, 'bajo'), (3,  'medio'), (6,  'alto'), (9999, 'muy_alto')],
        'D3':     [(1, 'bajo'), (3,  'medio'), (6,  'alto'), (9999, 'muy_alto')],
        'D4':     [(2, 'bajo'), (5,  'medio'), (8,  'alto'), (9999, 'muy_alto')],
        'D5':     [(0, 'bajo'), (2,  'medio'), (5,  'alto'), (9999, 'muy_alto')],
    },

    # ---- Guia III (16-50 trabajadores, 40 preguntas) ----
    'III': {
        'global': [(20, 'bajo'), (45, 'medio'), (70, 'alto'), (9999, 'muy_alto')],
        'D1':     [(2,  'bajo'), (5,  'medio'), (9,  'alto'), (9999, 'muy_alto')],
        'D2':     [(9,  'bajo'), (14, 'medio'), (19, 'alto'), (9999, 'muy_alto')],
        'D3':     [(2,  'bajo'), (4,  'medio'), (7,  'alto'), (9999, 'muy_alto')],
        'D4':     [(9,  'bajo'), (14, 'medio'), (24, 'alto'), (9999, 'muy_alto')],
        'D5':     [(9,  'bajo'), (14, 'medio'), (24, 'alto'), (9999, 'muy_alto')],
    },

    # ---- Guia V (>50 trabajadores, 55 preguntas) ----
    'V': {
        'global': [(20, 'bajo'), (45, 'medio'), (70, 'alto'), (9999, 'muy_alto')],
        'D1':     [(2,  'bajo'), (5,  'medio'), (9,  'alto'), (9999, 'muy_alto')],
        'D2':     [(9,  'bajo'), (14, 'medio'), (19, 'alto'), (9999, 'muy_alto')],
        'D3':     [(2,  'bajo'), (4,  'medio'), (7,  'alto'), (9999, 'muy_alto')],
        'D4':     [(2,  'bajo'), (5,  'medio'), (9,  'alto'), (9999, 'muy_alto')],
        'D5':     [(2,  'bajo'), (4,  'medio'), (7,  'alto'), (9999, 'muy_alto')],
        'D6':     [(9,  'bajo'), (19, 'medio'), (34, 'alto'), (9999, 'muy_alto')],
        'D7':     [(9,  'bajo'), (14, 'medio'), (24, 'alto'), (9999, 'muy_alto')],
    },
}


def get_categoria(guia_clave: str, key: str, puntaje: int) -> str:
    tbl = THRESHOLDS.get(guia_clave, {}).get(key, [(9999, 'bajo')])
    for max_val, cat in tbl:
        if puntaje <= max_val:
            return cat
    return 'muy_alto'


def calcular_resultado(aplicacion) -> dict:
    """
    Calcula puntajes y categorias para una Aplicacion completada.
    No persiste nada — devuelve un dict listo para crear/actualizar modelos.
    """
    respuestas = {r.pregunta_id: r for r in aplicacion.respuestas.all()}
    guia = aplicacion.cuestionario.clave

    dominios_result = []
    puntaje_total = 0
    puntaje_max_total = 0

    for dominio in aplicacion.cuestionario.dominios.prefetch_related('preguntas').all():
        puntaje = puntaje_max = 0
        for pregunta in dominio.preguntas.all():
            puntaje_max += 4
            if pregunta.id in respuestas:
                r = respuestas[pregunta.id]
                puntaje += (4 - r.valor) if pregunta.inversa else r.valor

        dominios_result.append({
            'dominio_id':     dominio.id,
            'dominio_clave':  dominio.clave,
            'dominio_nombre': dominio.nombre,
            'puntaje':        puntaje,
            'puntaje_max':    puntaje_max,
            'categoria':      get_categoria(guia, dominio.clave, puntaje),
        })
        puntaje_total     += puntaje
        puntaje_max_total += puntaje_max

    return {
        'puntaje_total': puntaje_total,
        'puntaje_max':   puntaje_max_total,
        'categoria':     get_categoria(guia, 'global', puntaje_total),
        'dominios':      dominios_result,
    }
