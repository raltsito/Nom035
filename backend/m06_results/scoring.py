"""
Motor de calificacion NOM-035-STPS-2018.

La Guia V del PDF actualizado contiene datos del trabajador y no genera nivel
de riesgo. La Guia I identifica necesidad de evaluacion clinica por
acontecimientos traumaticos severos. La Guia III usa los rangos oficiales de
la Guia de Referencia III para cuestionario de 72 reactivos.
"""


def _categoria_por_rangos(puntaje, limites):
    for max_exclusive, categoria in limites:
        if puntaje < max_exclusive:
            return categoria
    return 'muy_alto'


GUIA_III_GLOBAL = [
    (50, 'nulo'),
    (75, 'bajo'),
    (99, 'medio'),
    (140, 'alto'),
]

GUIA_III_DOMINIOS = {
    'D1': [(5, 'nulo'), (9, 'bajo'), (11, 'medio'), (14, 'alto')],
    'D2': [(15, 'nulo'), (21, 'bajo'), (27, 'medio'), (37, 'alto')],
    'D3': [(11, 'nulo'), (16, 'bajo'), (21, 'medio'), (25, 'alto')],
    'D4': [(1, 'nulo'), (2, 'bajo'), (4, 'medio'), (6, 'alto')],
    'D5': [(4, 'nulo'), (6, 'bajo'), (8, 'medio'), (10, 'alto')],
    'D6': [(9, 'nulo'), (12, 'bajo'), (16, 'medio'), (20, 'alto')],
    'D7': [(10, 'nulo'), (13, 'bajo'), (17, 'medio'), (21, 'alto')],
    'D8': [(7, 'nulo'), (10, 'bajo'), (13, 'medio'), (16, 'alto')],
    'D9': [(6, 'nulo'), (10, 'bajo'), (14, 'medio'), (18, 'alto')],
    'D10': [(4, 'nulo'), (6, 'bajo'), (8, 'medio'), (10, 'alto')],
}


def _valor_puntaje(respuesta, pregunta):
    if not respuesta or respuesta.valor is None:
        return 0
    return (4 - respuesta.valor) if pregunta.inversa else respuesta.valor


def _calcular_guia_i(aplicacion, respuestas):
    dominios_result = []
    puntaje_total = 0
    puntaje_max_total = 0
    hay_acontecimiento = False
    hay_sintoma = False

    for dominio in aplicacion.cuestionario.dominios.prefetch_related('preguntas').all():
        puntaje = 0
        preguntas = list(dominio.preguntas.all())
        for pregunta in preguntas:
            respuesta = respuestas.get(pregunta.id)
            if respuesta and respuesta.valor == 1:
                puntaje += 1

        if dominio.clave == 'D1':
            hay_acontecimiento = puntaje > 0
        else:
            hay_sintoma = hay_sintoma or puntaje > 0

        puntaje_total += puntaje
        puntaje_max_total += len(preguntas)
        dominios_result.append({
            'dominio_id': dominio.id,
            'dominio_clave': dominio.clave,
            'dominio_nombre': dominio.nombre,
            'puntaje': puntaje,
            'puntaje_max': len(preguntas),
            'categoria': 'alto' if dominio.clave != 'D1' and puntaje > 0 else 'bajo',
        })

    requiere_atencion = hay_acontecimiento and hay_sintoma
    return {
        'puntaje_total': puntaje_total,
        'puntaje_max': puntaje_max_total,
        'categoria': 'alto' if requiere_atencion else 'bajo',
        'dominios': dominios_result,
    }


def _calcular_guia_iii(aplicacion, respuestas):
    dominios_result = []
    puntaje_total = 0
    puntaje_max_total = 0

    for dominio in aplicacion.cuestionario.dominios.prefetch_related('preguntas').all():
        puntaje = 0
        puntaje_max = 0
        for pregunta in dominio.preguntas.all():
            if pregunta.tipo_respuesta != 'frecuencia':
                continue
            puntaje_max += 4
            puntaje += _valor_puntaje(respuestas.get(pregunta.id), pregunta)

        dominios_result.append({
            'dominio_id': dominio.id,
            'dominio_clave': dominio.clave,
            'dominio_nombre': dominio.nombre,
            'puntaje': puntaje,
            'puntaje_max': puntaje_max,
            'categoria': _categoria_por_rangos(
                puntaje,
                GUIA_III_DOMINIOS.get(dominio.clave, [(9999, 'nulo')]),
            ),
        })
        puntaje_total += puntaje
        puntaje_max_total += puntaje_max

    return {
        'puntaje_total': puntaje_total,
        'puntaje_max': puntaje_max_total,
        'categoria': _categoria_por_rangos(puntaje_total, GUIA_III_GLOBAL),
        'dominios': dominios_result,
    }


def calcular_resultado(aplicacion) -> dict | None:
    respuestas = {r.pregunta_id: r for r in aplicacion.respuestas.all()}
    guia = aplicacion.cuestionario.clave

    if guia == 'V':
        return None
    if guia == 'I':
        return _calcular_guia_i(aplicacion, respuestas)
    if guia == 'III':
        return _calcular_guia_iii(aplicacion, respuestas)

    return None
