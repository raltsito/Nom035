"""
Puebla la base de datos con los cuestionarios NOM-035-STPS-2018.
Guia I (<=15), Guia III (16-50), Guia V (51+).
Idempotente: puede ejecutarse varias veces sin duplicar datos.
"""
from django.core.management.base import BaseCommand
from m05_questionnaires.models import Cuestionario, Dominio, Pregunta

# ---------------------------------------------------------------------------
# Datos de los cuestionarios — estructura fija por NOM-035-STPS-2018
# Formato:  { clave, nombre, descripcion, tamano_min, tamano_max, dominios: [
#              { clave, nombre, preguntas: [ {texto, inversa?} ] }
#           ]}
# ---------------------------------------------------------------------------

CUESTIONARIOS = [

    # =========================================================
    # GUIA I — Centros de trabajo con hasta 15 trabajadores
    # =========================================================
    {
        'clave': 'I',
        'nombre': 'Identificacion de los factores de riesgo psicosocial',
        'descripcion': 'Cuestionario para centros de trabajo con hasta 15 trabajadores. '
                       'Evalua las condiciones del entorno laboral que pueden generar '
                       'factores de riesgo psicosocial.',
        'tamano_min': 1,
        'tamano_max': 15,
        'dominios': [
            {
                'clave': 'D1',
                'nombre': 'Condiciones en el ambiente de trabajo',
                'preguntas': [
                    {'texto': 'El espacio donde realizo mi trabajo es incomodo (poco espacio, mal ventilado, ruidoso, temperatura inadecuada u otros).'},
                    {'texto': 'Mi trabajo me exige realizar mucho esfuerzo fisico.'},
                    {'texto': 'Me preocupa sufrir un accidente o una enfermedad a causa de mi trabajo.'},
                    {'texto': 'Considero que las actividades que realizo son peligrosas.'},
                    {'texto': 'En mi trabajo se realizan labores peligrosas sin contar con equipo de proteccion adecuado.'},
                ],
            },
            {
                'clave': 'D2',
                'nombre': 'Carga y ritmo de trabajo',
                'preguntas': [
                    {'texto': 'Por la cantidad de trabajo que tengo debo quedarme tiempo extra.'},
                    {'texto': 'Por la cantidad de trabajo que tengo debo trabajar muy rapido.'},
                    {'texto': 'Mi trabajo me exige atender varios asuntos al mismo tiempo.'},
                    {'texto': 'Por la cantidad de trabajo que tengo no alcanzo a terminar en el horario establecido.'},
                ],
            },
            {
                'clave': 'D3',
                'nombre': 'Jornada y organizacion del tiempo de trabajo',
                'preguntas': [
                    {'texto': 'Trabajo horas extra mas de tres veces a la semana.'},
                    {'texto': 'Mi trabajo me exige laborar en dias de descanso, festivos o vacaciones.'},
                    {'texto': 'Tengo dificultad para tomar mis vacaciones o ausencias justificadas.'},
                    {'texto': 'Atiendo asuntos de trabajo cuando estoy de descanso o fuera del horario laboral.'},
                ],
            },
            {
                'clave': 'D4',
                'nombre': 'Liderazgo',
                'preguntas': [
                    {'texto': 'Mi jefe me da retroalimentacion sobre mi desempenio.', 'inversa': True},
                    {'texto': 'Mi jefe me impide tomar decisiones relacionadas con mi trabajo.'},
                    {'texto': 'Mi jefe me cambia de actividades o funciones sin avisarme con anticipacion.'},
                    {'texto': 'Mi jefe habla mal de mi delante de mis companeros de trabajo.'},
                    {'texto': 'Mi jefe me llama la atencion delante de mis companeros de trabajo.'},
                    {'texto': 'Mi jefe no respeta mis derechos laborales.'},
                ],
            },
            {
                'clave': 'D5',
                'nombre': 'Relaciones en el trabajo',
                'preguntas': [
                    {'texto': 'Mis companeros de trabajo dificultan o no facilitan la realizacion de mis actividades.'},
                    {'texto': 'Hay peleas, agresiones o problemas entre mis companeros de trabajo.'},
                    {'texto': 'He sido victima de actos de violencia o acoso laboral en mi trabajo.'},
                    {'texto': 'En mi trabajo existe discriminacion (por genero, edad, religion, preferencia sexual, origen etnico u otros).'},
                ],
            },
        ],
    },

    # =========================================================
    # GUIA III — Centros de trabajo de 16 a 50 trabajadores
    # =========================================================
    {
        'clave': 'III',
        'nombre': 'Identificacion de factores de riesgo psicosocial y evaluacion del entorno organizacional',
        'descripcion': 'Cuestionario para centros de trabajo de 16 a 50 trabajadores. '
                       'Evalua cinco dimensiones clave del entorno laboral conforme a la NOM-035-STPS-2018.',
        'tamano_min': 16,
        'tamano_max': 50,
        'dominios': [
            {
                'clave': 'D1',
                'nombre': 'Condiciones en el ambiente de trabajo',
                'preguntas': [
                    {'texto': 'El espacio donde realizo mi trabajo es incomodo (poco espacio, mal ventilado, ruidoso, temperatura inadecuada u otros).'},
                    {'texto': 'Mi trabajo me exige realizar mucho esfuerzo fisico.'},
                    {'texto': 'Me preocupa sufrir un accidente o una enfermedad a causa de mi trabajo.'},
                    {'texto': 'Considero que las actividades que realizo son peligrosas.'},
                    {'texto': 'En mi trabajo se realizan labores peligrosas sin contar con equipo de proteccion adecuado.'},
                    {'texto': 'Tengo que usar equipo de proteccion personal inadecuado o en mal estado.'},
                ],
            },
            {
                'clave': 'D2',
                'nombre': 'Factores propios de la actividad',
                'preguntas': [
                    {'texto': 'Por la cantidad de trabajo que tengo debo quedarme tiempo extra.'},
                    {'texto': 'Por la cantidad de trabajo que tengo debo trabajar muy rapido.'},
                    {'texto': 'Mi trabajo me exige atender varios asuntos al mismo tiempo.'},
                    {'texto': 'Mi trabajo exige que me mantenga muy concentrado durante un tiempo prolongado.'},
                    {'texto': 'Mi trabajo me exige memorizar mucha informacion.'},
                    {'texto': 'Mi trabajo me demanda tomar decisiones de manera inmediata.'},
                    {'texto': 'Mi trabajo me exige habilidades o conocimientos altamente especializados.'},
                    {'texto': 'Mi trabajo me hace sentir con exceso de responsabilidades.'},
                ],
            },
            {
                'clave': 'D3',
                'nombre': 'Organizacion del tiempo de trabajo',
                'preguntas': [
                    {'texto': 'Trabajo horas extra mas de tres veces a la semana.'},
                    {'texto': 'Mi trabajo me exige laborar en dias de descanso, festivos o vacaciones.'},
                    {'texto': 'Tengo dificultad para tomar mis vacaciones o ausencias justificadas.'},
                    {'texto': 'Atiendo asuntos de trabajo cuando estoy de descanso o fuera del horario laboral.'},
                    {'texto': 'Mi horario de trabajo me impide atender mis necesidades personales o familiares.'},
                    {'texto': 'Mi horario de trabajo cambia de manera inesperada.'},
                ],
            },
            {
                'clave': 'D4',
                'nombre': 'Liderazgo y relaciones en el trabajo',
                'preguntas': [
                    {'texto': 'Mi jefe me da retroalimentacion sobre mi desempenio.', 'inversa': True},
                    {'texto': 'Mi jefe me apoya cuando tengo dificultades en el trabajo.', 'inversa': True},
                    {'texto': 'Mi jefe asigna el trabajo de forma equitativa.', 'inversa': True},
                    {'texto': 'Mi jefe me impide tomar decisiones relacionadas con mi trabajo.'},
                    {'texto': 'Mi jefe me cambia de actividades sin avisarme con anticipacion.'},
                    {'texto': 'Mi jefe habla mal de mi delante de mis companeros.'},
                    {'texto': 'Mi jefe me llama la atencion delante de otros trabajadores.'},
                    {'texto': 'Mi jefe no respeta mis derechos laborales.'},
                    {'texto': 'Mis companeros de trabajo colaboran conmigo para realizar nuestras actividades.', 'inversa': True},
                    {'texto': 'En mi trabajo existen problemas o conflictos entre companeros.'},
                    {'texto': 'He sido victima de acoso o violencia laboral en mi trabajo.'},
                    {'texto': 'He sido testigo de actos de violencia o acoso hacia mis companeros.'},
                ],
            },
            {
                'clave': 'D5',
                'nombre': 'Entorno organizacional',
                'preguntas': [
                    {'texto': 'Mi trabajo me ofrece oportunidades de desarrollo profesional.', 'inversa': True},
                    {'texto': 'Recibo la capacitacion que necesito para realizar bien mi trabajo.', 'inversa': True},
                    {'texto': 'En mi trabajo se reconoce el desempenio sobresaliente.', 'inversa': True},
                    {'texto': 'Mi trabajo me permite obtener logros que son valorados.', 'inversa': True},
                    {'texto': 'En mi trabajo se informa claramente sobre los cambios en las politicas o procedimientos.', 'inversa': True},
                    {'texto': 'Las condiciones de mi contratacion (salario, prestaciones, tipo de contrato) me generan incertidumbre.'},
                    {'texto': 'Me preocupa perder mi trabajo.'},
                    {'texto': 'En mi trabajo existe discriminacion (por genero, edad, origen etnico, religion u otros).'},
                ],
            },
        ],
    },

    # =========================================================
    # GUIA V — Centros de trabajo con mas de 50 trabajadores
    # =========================================================
    {
        'clave': 'V',
        'nombre': 'Identificacion de factores de riesgo psicosocial, evaluacion del entorno organizacional y eventos traumaticos severos',
        'descripcion': 'Cuestionario para centros de trabajo con mas de 50 trabajadores. '
                       'Version completa conforme a la NOM-035-STPS-2018.',
        'tamano_min': 51,
        'tamano_max': None,
        'dominios': [
            {
                'clave': 'D1',
                'nombre': 'Condiciones en el ambiente de trabajo',
                'preguntas': [
                    {'texto': 'El espacio donde realizo mi trabajo es incomodo (poco espacio, mal ventilado, ruidoso, temperatura inadecuada u otros).'},
                    {'texto': 'Mi trabajo me exige realizar mucho esfuerzo fisico.'},
                    {'texto': 'Me preocupa sufrir un accidente o una enfermedad a causa de mi trabajo.'},
                    {'texto': 'Considero que las actividades que realizo son peligrosas.'},
                    {'texto': 'En mi trabajo se realizan labores peligrosas sin contar con equipo de proteccion adecuado.'},
                    {'texto': 'Tengo que usar equipo de proteccion personal inadecuado o en mal estado.'},
                    {'texto': 'Estoy expuesto a sustancias quimicas, biologicas u otros agentes daninios para la salud.'},
                ],
            },
            {
                'clave': 'D2',
                'nombre': 'Carga de trabajo',
                'preguntas': [
                    {'texto': 'Por la cantidad de trabajo que tengo debo quedarme tiempo extra.'},
                    {'texto': 'Por la cantidad de trabajo que tengo debo trabajar muy rapido.'},
                    {'texto': 'Mi trabajo me exige atender varios asuntos al mismo tiempo.'},
                    {'texto': 'Mi trabajo exige que me mantenga muy concentrado durante tiempo prolongado.'},
                    {'texto': 'Mi trabajo me exige memorizar mucha informacion.'},
                    {'texto': 'Mi trabajo me demanda tomar decisiones de manera inmediata.'},
                    {'texto': 'Mi trabajo me exige habilidades o conocimientos altamente especializados.'},
                    {'texto': 'Mi trabajo me hace sentir con exceso de responsabilidades.'},
                ],
            },
            {
                'clave': 'D3',
                'nombre': 'Falta de control sobre el trabajo',
                'preguntas': [
                    {'texto': 'Mi trabajo me permite escoger como realizar mis actividades.', 'inversa': True},
                    {'texto': 'Tengo posibilidad de tomar decisiones sobre el ritmo de mi trabajo.', 'inversa': True},
                    {'texto': 'Puedo elegir el orden en que realizo mis actividades de trabajo.', 'inversa': True},
                    {'texto': 'Mi trabajo me permite desarrollar nuevas habilidades.', 'inversa': True},
                    {'texto': 'Tengo autonomia para resolver los problemas que se presentan en mi trabajo.', 'inversa': True},
                ],
            },
            {
                'clave': 'D4',
                'nombre': 'Jornada y organizacion del tiempo de trabajo',
                'preguntas': [
                    {'texto': 'Trabajo horas extra mas de tres veces a la semana.'},
                    {'texto': 'Mi trabajo me exige laborar en dias de descanso, festivos o vacaciones.'},
                    {'texto': 'Tengo dificultad para tomar mis vacaciones o ausencias justificadas.'},
                    {'texto': 'Atiendo asuntos de trabajo cuando estoy de descanso o fuera del horario laboral.'},
                    {'texto': 'Mi horario de trabajo me impide atender mis necesidades personales o familiares.'},
                    {'texto': 'Mi horario de trabajo cambia de manera inesperada.'},
                    {'texto': 'El trabajo que realizo fuera de la jornada no es reconocido ni remunerado.'},
                ],
            },
            {
                'clave': 'D5',
                'nombre': 'Interferencia en la relacion trabajo-familia',
                'preguntas': [
                    {'texto': 'Las exigencias de mi trabajo interfieren en mi vida personal y familiar.'},
                    {'texto': 'Las responsabilidades de mi trabajo me dificultan cumplir con mis obligaciones familiares.'},
                    {'texto': 'El trabajo me impide dedicar tiempo suficiente a mi familia o vida personal.'},
                    {'texto': 'Debo atender llamadas, mensajes o correos del trabajo en horarios de descanso.'},
                ],
            },
            {
                'clave': 'D6',
                'nombre': 'Liderazgo y relaciones en el trabajo',
                'preguntas': [
                    {'texto': 'Mi jefe me da retroalimentacion sobre mi desempenio.', 'inversa': True},
                    {'texto': 'Mi jefe me apoya cuando tengo dificultades en el trabajo.', 'inversa': True},
                    {'texto': 'Mi jefe asigna el trabajo de forma equitativa.', 'inversa': True},
                    {'texto': 'Mi jefe me informa con claridad sobre los objetivos y resultados esperados.', 'inversa': True},
                    {'texto': 'Mi jefe impide mi participacion en las decisiones de mi trabajo.'},
                    {'texto': 'Mi jefe me cambia de actividades o funciones sin avisarme.'},
                    {'texto': 'Mi jefe habla mal de mi delante de mis companeros.'},
                    {'texto': 'Mi jefe me llama la atencion delante de otros trabajadores.'},
                    {'texto': 'Mi jefe no respeta mis derechos laborales.'},
                    {'texto': 'Mis companeros de trabajo colaboran conmigo.', 'inversa': True},
                    {'texto': 'Cuento con el apoyo de mis companeros cuando lo necesito.', 'inversa': True},
                    {'texto': 'En mi trabajo existen conflictos o peleas entre companeros.'},
                    {'texto': 'He sido victima de acoso o violencia laboral.'},
                    {'texto': 'He presenciado actos de violencia o acoso hacia otros companeros.'},
                ],
            },
            {
                'clave': 'D7',
                'nombre': 'Entorno organizacional y reconocimiento',
                'preguntas': [
                    {'texto': 'Mi trabajo me ofrece oportunidades de desarrollo profesional.', 'inversa': True},
                    {'texto': 'Recibo la capacitacion que necesito para realizar bien mi trabajo.', 'inversa': True},
                    {'texto': 'En mi trabajo se reconoce el desempenio sobresaliente.', 'inversa': True},
                    {'texto': 'Mi trabajo me permite obtener logros que son valorados.', 'inversa': True},
                    {'texto': 'Se informa con claridad sobre los cambios en politicas, procedimientos o restructuraciones.', 'inversa': True},
                    {'texto': 'Participo en las decisiones que afectan mis condiciones de trabajo.', 'inversa': True},
                    {'texto': 'Las condiciones de mi contratacion me generan incertidumbre.'},
                    {'texto': 'Me preocupa perder mi trabajo.'},
                    {'texto': 'En mi trabajo existe discriminacion (por genero, edad, origen etnico, religion, preferencia sexual u otros).'},
                    {'texto': 'Mi salario o prestaciones no corresponden con el trabajo que realizo.'},
                ],
            },
        ],
    },
]

from .cuestionarios_actualizados import CUESTIONARIOS


class Command(BaseCommand):
    help = 'Siembra los cuestionarios NOM-035 (Guias I, III y V) en la base de datos.'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando seed de cuestionarios NOM-035...')

        for data in CUESTIONARIOS:
            cuestionario, created = Cuestionario.objects.update_or_create(
                clave=data['clave'],
                defaults={
                    'nombre':      data['nombre'],
                    'descripcion': data['descripcion'],
                    'tamano_min':  data['tamano_min'],
                    'tamano_max':  data['tamano_max'],
                },
            )
            status = 'CREADO' if created else 'ACTUALIZADO'
            self.stdout.write(f'  Guia {cuestionario.clave} [{status}]')

            dominios_validos = set()
            preguntas_por_ref = {}
            condiciones_pendientes = []
            for dom_orden, dom_data in enumerate(data['dominios'], start=1):
                dominio, _ = Dominio.objects.update_or_create(
                    cuestionario=cuestionario,
                    orden=dom_orden,
                    defaults={
                        'clave':  dom_data['clave'],
                        'nombre': dom_data['nombre'],
                    },
                )
                dominios_validos.add(dominio.id)

                preguntas_validas = set()
                for preg_orden, preg_data in enumerate(dom_data['preguntas'], start=1):
                    pregunta, _ = Pregunta.objects.update_or_create(
                        dominio=dominio,
                        orden=preg_orden,
                        defaults={
                            'texto':   preg_data['texto'],
                            'inversa': preg_data.get('inversa', False),
                            'tipo_respuesta': preg_data.get('tipo_respuesta', 'frecuencia'),
                            'opciones': preg_data.get('opciones', []),
                            'condicion_pregunta': None,
                            'condicion_valor': preg_data.get('condicion_valor'),
                            'condicion_operador': preg_data.get('condicion_operador', 'all'),
                        },
                    )
                    pregunta.condicion_preguntas.clear()
                    preguntas_validas.add(pregunta.id)
                    if preg_data.get('ref'):
                        preguntas_por_ref[preg_data['ref']] = pregunta
                    if preg_data.get('condicion_refs'):
                        condiciones_pendientes.append((pregunta, preg_data['condicion_refs']))

                Pregunta.objects.filter(dominio=dominio).exclude(id__in=preguntas_validas).delete()

                total = len(dom_data['preguntas'])
                self.stdout.write(f'    {dominio.clave}: {dominio.nombre} ({total} preguntas)')

            Dominio.objects.filter(cuestionario=cuestionario).exclude(id__in=dominios_validos).delete()

            for pregunta, refs in condiciones_pendientes:
                pregunta.condicion_preguntas.set(
                    preguntas_por_ref[ref] for ref in refs if ref in preguntas_por_ref
                )

        total_preguntas = sum(
            len(p['preguntas'])
            for c in CUESTIONARIOS for p in c['dominios']
        )
        self.stdout.write(self.style.SUCCESS(
            f'\nSeed completado. {len(CUESTIONARIOS)} cuestionarios, {total_preguntas} preguntas en total.'
        ))
