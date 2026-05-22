"""
Pre-llenado automático de la Guía V desde los campos del trabajador.

Mapa: orden de pregunta → campo del modelo Trabajador → valor normalizado
"""

from datetime import date
from django.db import transaction

from .models import Cuestionario, Pregunta, RespuestaPregunta

# ---------------------------------------------------------------------------
# Tablas de conversión
# ---------------------------------------------------------------------------

_SEXO = {'M': 'Masculino', 'F': 'Femenino'}

_ESTADO_CIVIL = {
    'soltero':    'Soltero',
    'casado':     'Casado',
    'union_libre': 'Union libre',
    'divorciado': 'Divorciado',
    'viudo':      'Viudo',
}

_NIVEL = {
    'primaria':     'Primaria',
    'secundaria':   'Secundaria',
    'bachillerato': 'Preparatoria',
    'tecnico':      'Tecnico superior',
    'licenciatura': 'Licenciatura',
    'ingenieria':   'Licenciatura',
    'posgrado':     'Maestria',
}

_CONTRAT = {
    'planta':         'Tiempo indeterminado',
    'eventual':       'Por tiempo determinado temporal',
    'subcontratado':  'Por obra o proyecto',
}

_PERSONAL = {
    'sindicalizado': 'Sindicalizado',
    'confianza':     'Confianza',
    'salary':        'Ninguno',
    'otro':          'Ninguno',
}

_JORNADA = {
    'diurno':   'Fijo diurno',
    'nocturno': 'Fijo nocturno',
    'mixto':    'Fijo mixto',
}

_TIPO_PUESTO_OPCIONES = {
    'operativo':   'Operativo',
    'supervisor':  'Supervisor',
    'profesional': 'Profesional o tecnico',
    'tecnico':     'Profesional o tecnico',
    'gerente':     'Gerente',
    'director':    'Gerente',
}


def _match_tipo_puesto(raw):
    if not raw:
        return None
    v = raw.lower()
    for key, opcion in _TIPO_PUESTO_OPCIONES.items():
        if key in v:
            return opcion
    return None


def _build_responses(trabajador):
    """
    Devuelve {orden: (valor, valor_texto)} para cada campo del trabajador que esté lleno.
    valor      → entero para si_no/frecuencia, None para texto/opcion
    valor_texto → string para texto/opcion, '' para si_no/frecuencia
    """
    r = {}

    # P1 Nombre completo
    nc = trabajador.nombre_completo
    if nc:
        r[1] = (None, nc)

    # P2 Fecha
    r[2] = (None, date.today().strftime('%d/%m/%Y'))

    # P3 Sexo (opcion)
    v = _SEXO.get(trabajador.sexo)
    if v:
        r[3] = (None, v)

    # P4 Edad (texto)
    if trabajador.edad is not None:
        r[4] = (None, str(trabajador.edad))

    # P5 Estado civil (opcion)
    v = _ESTADO_CIVIL.get(trabajador.estado_civil)
    if v:
        r[5] = (None, v)

    # P6 Nivel de estudios (opcion)
    v = _NIVEL.get(trabajador.nivel_estudios)
    if v:
        r[6] = (None, v)

    # P7 Puesto (texto)
    if trabajador.puesto:
        r[7] = (None, trabajador.puesto.strip())

    # P8 Área (texto)
    if trabajador.area:
        r[8] = (None, trabajador.area.strip())

    # P9 Tipo de puesto (opcion - texto libre → match)
    v = _match_tipo_puesto(trabajador.tipo_puesto)
    if v:
        r[9] = (None, v)

    # P10 Tipo de contratación (opcion)
    v = _CONTRAT.get(trabajador.tipo_contratacion)
    if v:
        r[10] = (None, v)

    # P11 Tipo de personal (opcion)
    v = _PERSONAL.get(trabajador.tipo_personal)
    if v:
        r[11] = (None, v)

    # P12 Tipo de jornada (opcion)
    v = _JORNADA.get(trabajador.tipo_jornada)
    if v:
        r[12] = (None, v)

    # P13 Rotación de turnos (si_no → 1/0)
    if trabajador.rotacion_turnos is not None:
        r[13] = (1 if trabajador.rotacion_turnos else 0, '')

    # P14 Experiencia en puesto actual (texto)
    if trabajador.tiempo_puesto_actual is not None:
        r[14] = (None, str(trabajador.tiempo_puesto_actual))

    # P15 Experiencia laboral total (texto)
    if trabajador.experiencia_anios is not None:
        r[15] = (None, str(trabajador.experiencia_anios))

    return r


def get_prefilled_question_ids(trabajador):
    """
    Devuelve el conjunto de IDs de preguntas de la Guía V que tienen
    correspondencia con campos llenos del trabajador.
    Usado por el serializer para informar al frontend qué preguntas ocultar.
    """
    try:
        cuestionario = Cuestionario.objects.get(clave='V')
    except Cuestionario.DoesNotExist:
        return set()

    preguntas = {
        p.orden: p.id
        for p in Pregunta.objects.filter(dominio__cuestionario=cuestionario)
    }
    responses = _build_responses(trabajador)
    return {preguntas[orden] for orden in responses if orden in preguntas}


@transaction.atomic
def prefill_guia_v(aplicacion, trabajador):
    """
    Pre-llena las RespuestaPregunta de la Guía V con los datos del trabajador.
    Solo crea respuestas para preguntas que no tienen respuesta previa.
    Si al terminar todas las preguntas están respondidas, marca la aplicación
    como completada.
    """
    try:
        cuestionario = Cuestionario.objects.get(clave='V')
    except Cuestionario.DoesNotExist:
        return

    preguntas = {
        p.orden: p
        for p in Pregunta.objects.filter(dominio__cuestionario=cuestionario)
    }
    ya_respondidas = set(aplicacion.respuestas.values_list('pregunta_id', flat=True))
    responses = _build_responses(trabajador)

    for orden, (valor, valor_texto) in responses.items():
        pregunta = preguntas.get(orden)
        if not pregunta or pregunta.id in ya_respondidas:
            continue
        RespuestaPregunta.objects.create(
            aplicacion=aplicacion,
            pregunta=pregunta,
            tenant=aplicacion.tenant,
            valor=valor,
            valor_texto=valor_texto or '',
        )

    total = len(preguntas)
    respondidas = aplicacion.respuestas.count()
    if total and respondidas >= total:
        aplicacion.marcar_completado()
    elif aplicacion.estado == 'pendiente' and respondidas > 0:
        aplicacion.estado = 'en_progreso'
        aplicacion.save(update_fields=['estado'])
