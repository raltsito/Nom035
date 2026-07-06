"""
Contenido normativo fijo del reporte psicológico NOM-035-STPS-2018, transcrito de
los Apartados 3-6 de la Guía de Referencia y del documento estándar de formato
(INFORME DIAGNOSTICO NOM035 LEAR TLÁHUAC.pdf), que esta plantilla sigue al 100%.

No depende del tenant ni del ciclo — es el mismo texto para cualquier cliente.
Se consume desde `documents/views.py` y se renderiza en
`documents/templates/documents/reporte_psicologico.html`.
"""

OBJETIVO_GENERAL = (
    'El objetivo de este informe es identificar, analizar y prevenir los factores de '
    'riesgo psicosocial en los centros de trabajo, con el fin de promover un entorno '
    'organizacional favorable. Se busca el cumplimiento de la Norma Oficial Mexicana '
    'NOM-035-STPS-2018, Factores de riesgo psicosocial en el trabajo-Identificación, '
    'análisis y prevención, para implementar medidas de prevención y control que '
    'favorezcan la calidad de vida laboral y estableciendo un ambiente de trabajo seguro '
    'y productivo, que beneficie tanto la eficiencia como la satisfacción laboral de los '
    'trabajadores.'
)

OBJETIVOS_ESPECIFICOS = [
    'Identificar a los trabajadores que fueron sujetos a acontecimientos traumáticos '
    'severos o a actos de violencia laboral.',
    'Identificar y analizar los puestos de trabajo con factores de riesgo psicosocial '
    'por la naturaleza de sus funciones.',
    'Realizar evaluaciones del Entorno Organizacional Favorable, aplicables a Centros '
    'de Trabajo que cuenten con más de 50 trabajadores.',
    'Identificar y analizar los factores de riesgo psicosocial, que incluye: '
    'Condiciones en el ambiente de trabajo, Cargas de trabajo, Falta de control sobre '
    'el trabajo, Jornada de trabajo, Interferencia en la relación trabajo-familia, '
    'Liderazgo, Relaciones en el trabajo, Violencia laboral, Reconocimiento del '
    'desempeño e Insuficiente sentido de pertenencia e inestabilidad.',
    'Proponer medidas preventivas mediante el análisis cuantitativo para mitigar los '
    'factores de riesgo psicosocial.',
    'Identificar al personal que requiera exámenes o evaluaciones clínicas, '
    'ocupacionalmente expuesto a factores de riesgo psicosocial o violencia laboral.',
    'Generar un informe diagnóstico para informar a los trabajadores sobre las '
    'posibles alteraciones a la salud por la exposición a factores de riesgo '
    'psicosocial.',
]

DEFINICIONES = [
    ('Acontecimiento traumático severo (ATS)',
     'Acontecimiento experimentado durante o con motivo del trabajo, caracterizado por '
     'la muerte o peligro real para la integridad física de personas, que puede generar '
     'trastorno de estrés postraumático. Ejemplos incluyen explosiones, derrumbes, '
     'incendios, accidentes graves, asaltos con violencia, secuestros, homicidios, '
     'entre otros.'),
    ('Centro de trabajo',
     'Lugar o lugares donde se realizan actividades de explotación, producción, '
     'comercialización, transporte, almacenamiento o prestación de servicios, con '
     'personas sujetas a una relación laboral.'),
    ('Entorno Organizacional Favorable (EOL)',
     'Ambiente en el que se promueve el sentido de pertenencia, la adecuada formación, '
     'la precisa definición de responsabilidades, participación proactiva, '
     'comunicación entre trabajadores, distribución adecuada de cargas de trabajo y '
     'reconocimiento del desempeño.'),
    ('Factores de Riesgo Psicosocial (FRPs)',
     'Factores que pueden provocar trastornos de ansiedad, estrés o de adaptación, '
     'derivados de las funciones del puesto de trabajo, tipo de jornada, exposición a '
     'acontecimientos traumáticos o violencia laboral. Incluyen condiciones '
     'peligrosas, cargas de trabajo excesivas, falta de control sobre el trabajo, '
     'jornadas prolongadas, interferencia trabajo-familia, liderazgo negativo y '
     'relaciones laborales negativas.'),
    ('Política de prevención de riesgos psicosociales',
     'Declaración de principios y compromisos del patrón para prevenir los factores de '
     'riesgo psicosocial y violencia laboral, promoviendo un entorno organizacional '
     'favorable y procurando trabajo digno y mejora continua de las condiciones '
     'laborales.'),
    ('Trabajador/Colaborador',
     'Persona física que presta a otra (física o moral) un trabajo personal '
     'subordinado.'),
    ('Trabajo',
     'Toda actividad humana, intelectual o material, independientemente del grado de '
     'preparación técnica requerido.'),
    ('Violencia laboral',
     'Actos de hostigamiento, acoso o malos tratos en contra del trabajador, que '
     'pueden dañar su integridad o salud.'),
]

JUSTIFICACION_MUESTRA_INTRO = (
    'La muestra fue seleccionada de manera aleatoria, con el objetivo de incluir la '
    'participación de todos los departamentos que conforman el centro de trabajo y '
    'así incluir una percepción de mayor amplitud de la situación actual de la '
    'empresa.'
)

METODOLOGIA = {
    'objetivo_evaluacion': (
        'Definir los criterios de la toma de decisiones encaminadas a corregir y/o '
        'prevenir consecuencias que puedan desencadenarse por los factores de riesgo, '
        'mediante la cuantificación para la Identificación, Análisis y Prevención de '
        'los Factores de Riesgo Psicosocial y Evaluación del Entorno Organizacional en '
        'los Centros de Trabajo, estipulados en la Norma Oficial Mexicana '
        'NOM-035-STPS-2018, y brindar atención a todos aquellos colaboradores sujetos a '
        'acontecimientos traumáticos severos que pongan en riesgo su salud. La '
        'validación se realiza en trabajadores cuyos centros de trabajo se ubican en '
        'el territorio nacional.'
    ),
    'instrumentos': [
        ('Guía de Referencia V (NOM-035-STPS-2018)',
         'Datos del trabajador. Mediante el cual define la identidad del encuestado.'),
        ('Guía de Referencia III (NOM-035-STPS-2018)',
         'Cuestionario para identificar los factores de riesgo psicosocial y evaluar '
         'el entorno organizacional en los centros de trabajo.'),
        ('Guía de Referencia I (NOM-035-STPS-2018)',
         'Cuestionario para identificar a trabajadores que fueron sujetos a '
         'acontecimientos traumáticos severos.'),
    ],
    'procedimiento_antes': [
        'Se determinó el número mínimo de trabajadores a los que se les aplicarían '
        'los cuestionarios, asegurándose de que correspondiera al tamaño de la '
        'muestra, mediante la Ecuación 1 de la NORMA Oficial Mexicana NOM-035-STPS-2018.',
        'Se verificó que las condiciones de las instalaciones y del mobiliario fueran '
        'idóneas.',
        'Se realizó la presentación del aplicador ante las personas a evaluar.',
        'Se explicó el objetivo de la evaluación.',
        'Se enfatizó en la protección de la privacidad y confidencialidad del manejo '
        'de los datos, asegurando que el uso de la información proporcionada por el '
        'trabajador y de sus resultados sería exclusivamente para fines de mejora del '
        'ambiente de trabajo.',
        'Se dieron instrucciones claras sobre la forma de responder a las preguntas de '
        'las diferentes secciones, asegurándose de que el cuestionario fuera '
        'contestado completamente, destacando que no existían respuestas correctas o '
        'incorrectas, y se instó a los trabajadores a responder con sinceridad '
        'considerando las condiciones de los dos últimos meses.',
    ],
    'procedimiento_durante': [
        'Se propició un ambiente de respeto y confianza.',
        'Se permitió una comunicación fluida entre los trabajadores y el evaluador.',
        'Se aclararon dudas y se brindó apoyo a los trabajadores que lo requirieron.',
        'Se verificó que las indicaciones proporcionadas fueran claras.',
        'Se evitó interrumpir a los trabajadores mientras respondían.',
        'Se evitó conducir, persuadir o dirigir las respuestas.',
    ],
    'procedimiento_despues': [
        'Se recogió cada cuestionario y se verificó que fueran respondidos '
        'completamente, sin tachaduras o enmendaduras.',
        'Se comprobó que la cantidad de cuestionarios entregados correspondiera con la '
        'cantidad de cuestionarios respondidos y que, a su vez, coincidiera con el '
        'tamaño mínimo de la muestra.',
    ],
    'orden_aplicacion': [
        'Guía de Referencia III: Cuestionario para identificar los Factores de Riesgo '
        'Psicosocial.',
        'Guía de Referencia I: Cuestionario para identificar a trabajadores que fueron '
        'sujetos a acontecimientos traumáticos severos.',
        'Guía de Referencia V: Datos del trabajador.',
    ],
    'procesamiento_digital': (
        'Las respuestas obtenidas de los cuestionarios, aplicados de manera escrita y '
        'directa a los encuestados, son registradas en una base de datos utilizando '
        'tecnología de reconocimiento óptico de caracteres (OCR). Posteriormente, '
        'estos registros son sometidos a un proceso de auditoría para garantizar la '
        'precisión y exactitud de los datos capturados.'
    ),
    'evaluacion_analisis': (
        'La evaluación y cuantificación se lleva a cabo mediante procedimientos '
        'informáticos, conforme a lo establecido en la NOM-035-STPS-2018. Basándose en '
        'la información registrada en la base de datos, se realizan las combinaciones '
        'estipuladas en la normativa para cuantificar cada categoría, dominio y '
        'dimensión. A partir de estos cálculos, se obtienen conclusiones que guiarán '
        'las decisiones necesarias para corregir y/o prevenir las posibles '
        'consecuencias derivadas de los riesgos identificados.'
    ),
}

# ---------------------------------------------------------------------------
# Jerarquía oficial Categoría → Dominio (Tabla 6, Guía de Referencia III,
# NOM-035-STPS-2018, versión extendida para centros de >50 trabajadores).
# Cada dominio oficial agrupa uno o más de los 14 dominios (D1-D14) que el
# sistema ya califica (ver `m06_results/scoring.py`); estos últimos se
# presentan como "Dimensiones" en la sección 9.4, al ser el nivel de
# desagregación más fino con el que cuenta el sistema.
# D13 y D14 son dominios condicionales (atención a clientes / actitudes de
# supervisados) que solo se califican para los trabajadores a quienes aplican.
# ---------------------------------------------------------------------------
CATEGORIA_ESTRUCTURA = [
    ('Ambiente de trabajo', [
        ('Condiciones en el ambiente de trabajo', ['D1']),
    ]),
    ('Factores propios de la actividad', [
        ('Carga de trabajo', ['D2', 'D3', 'D4']),
        ('Falta de control sobre el trabajo', ['D6', 'D7', 'D8']),
        ('Atención a clientes', ['D13']),
    ]),
    ('Organización del tiempo de trabajo', [
        ('Jornada de trabajo e interferencia trabajo-familia', ['D5']),
    ]),
    ('Liderazgo y relaciones en el trabajo', [
        ('Liderazgo', ['D9']),
        ('Relaciones en el trabajo', ['D10']),
        ('Violencia', ['D12']),
        ('Actitudes de supervisados', ['D14']),
    ]),
    ('Entorno organizacional', [
        ('Reconocimiento del desempeño e inestabilidad', ['D11']),
    ]),
]

DOMINIO_CATEGORIA = {}
DOMINIO_OFICIAL_DE = {}
for _categoria, _dominios in CATEGORIA_ESTRUCTURA:
    for _dominio_oficial, _claves in _dominios:
        for _clave in _claves:
            DOMINIO_CATEGORIA[_clave] = _categoria
            DOMINIO_OFICIAL_DE[_clave] = _dominio_oficial

TABLA_AGRUPACION_DOMINIOS = [
    {'categoria': cat, 'dominio': dom, 'claves': claves}
    for cat, dominios in CATEGORIA_ESTRUCTURA
    for dom, claves in dominios
]

# ---------------------------------------------------------------------------
# Recomendaciones específicas por dominio (Informe Diagnóstico extendido,
# sección 11). Un bloque de 5-7 acciones concretas por cada uno de los 10
# dominios oficiales — se aplican solo a los dominios que el ciclo evaluado
# realmente clasificó en nivel de intervención (ver `_recomendaciones_desde_
# dominios` en views.py, activado con `informe_extendido=True`).
# Las claves deben coincidir exactamente con los nombres de dominio oficial
# usados en `CATEGORIA_ESTRUCTURA`.
# ---------------------------------------------------------------------------
RECOMENDACIONES_DOMINIO = {
    'Condiciones en el ambiente de trabajo': {
        'intro': (
            'En el sector industrial, las condiciones físicas del ambiente de '
            'trabajo impactan directamente en la seguridad, la salud y el '
            'rendimiento de los colaboradores.'
        ),
        'bullets': [
            ('Evaluación ergonómica de los puestos de trabajo',
             'Realizar una revisión sistemática de la postura, herramientas y equipos '
             'utilizados en cada puesto, corrigiendo factores que puedan generar '
             'sobrecarga física o riesgo de lesiones musculoesqueléticas.'),
            ('Control de ruido, iluminación y temperatura',
             'Medir periódicamente los niveles de ruido, iluminación y temperatura en '
             'las áreas de trabajo, implementando las mejoras técnicas necesarias para '
             'mantenerlos dentro de los límites normativos.'),
            ('Programa de mantenimiento preventivo de instalaciones',
             'Establecer un calendario de mantenimiento preventivo de maquinaria, '
             'equipos e instalaciones para reducir fallas que generen condiciones '
             'inseguras o interrupciones en el flujo de trabajo.'),
            ('Orden y limpieza bajo metodología 5S',
             'Implementar o reforzar la metodología 5S en todas las áreas de '
             'producción, asegurando espacios ordenados, limpios y libres de '
             'obstáculos que puedan representar un riesgo físico.'),
            ('Espacios dignos de descanso y servicios',
             'Asegurar que los comedores, sanitarios y áreas de descanso se '
             'encuentren en condiciones óptimas de higiene y comodidad, '
             'contribuyendo al bienestar integral del colaborador.'),
            ('Fortalecer la cultura de reporte de condiciones inseguras',
             'Implementar un mecanismo accesible y sin represalias para que los '
             'colaboradores reporten condiciones físicas de riesgo, con seguimiento '
             'documentado y tiempos de respuesta comprometidos.'),
        ],
    },
    'Carga de trabajo': {
        'intro': (
            'Una gestión adecuada de la carga de trabajo es esencial para preservar '
            'la salud de los colaboradores y mantener los estándares de calidad y '
            'productividad del centro de trabajo.'
        ),
        'bullets': [
            ('Redistribuir responsabilidades de manera equitativa',
             'Asegurarse de que la carga laboral esté balanceada entre todos los '
             'trabajadores, evitando la sobrecarga en ciertos puestos clave o '
             'empleados específicos, lo que mejorará tanto la eficiencia como la '
             'moral del equipo.'),
            ('Automatizar procesos repetitivos',
             'Implementar tecnologías automatizadas en tareas repetitivas dentro de '
             'la línea de producción, permitiendo a los empleados concentrarse en '
             'labores más críticas y de valor añadido, reduciendo la fatiga.'),
            ('Monitorear la carga de trabajo continuamente',
             'Realizar evaluaciones periódicas de la carga laboral en las diferentes '
             'etapas de la línea de producción, ajustando las asignaciones en función '
             'de la demanda y capacidades reales del equipo.'),
            ('Contratar personal adicional en picos de demanda',
             'Durante momentos de alta demanda, aumentar temporalmente la plantilla '
             'para aliviar la presión sobre los trabajadores permanentes y evitar '
             'retrasos en las entregas.'),
            ('Establecer límites claros a las horas de trabajo',
             'Regular el uso de horas extras y asegurar que los empleados tomen '
             'descansos adecuados durante la jornada para prevenir la fatiga, '
             'lo que es crucial donde la precisión y seguridad son fundamentales.'),
            ('Fortalecer los otros dominios',
             'Se recomiendan estudios periódicos de tiempo y carga de trabajo; '
             'mejorar los mecanismos de delegación de actividades, capacitación en '
             'objetivos del puesto o KPI/OKR; capacitar a los colaboradores en la '
             'organización del tiempo y las actividades.'),
        ],
    },
    'Falta de control sobre el trabajo': {
        'intro': (
            'Empoderar a los empleados para que tengan mayor control sobre su '
            'trabajo mejora tanto su satisfacción como la productividad del centro '
            'de trabajo.'
        ),
        'bullets': [
            ('Delegación de responsabilidades',
             'Distribuir las tareas de manera equitativa entre los empleados, '
             'otorgando mayor autonomía en la toma de decisiones dentro de su '
             'ámbito laboral.'),
            ('Formación continua',
             'Implementar programas de capacitación técnica y de gestión que '
             'fortalezcan las habilidades de los trabajadores, permitiéndoles tomar '
             'decisiones informadas y oportunas en el día a día.'),
            ('Uso de herramientas digitales de gestión',
             'Incorporar software que permita a los empleados organizar sus tareas, '
             'priorizar actividades y gestionar su carga de trabajo de manera '
             'más eficiente.'),
            ('Participación en la toma de decisiones',
             'Fomentar que los trabajadores participen activamente en la mejora de '
             'procesos productivos, dándoles voz en las decisiones operativas.'),
            ('Retroalimentación constante',
             'Proporcionar comentarios frecuentes y constructivos para que los '
             'empleados ajusten su desempeño según los objetivos y estándares de '
             'calidad de la empresa.'),
            ('Plan de capacitación',
             'Mejorar/implementar planes de capacitación por colaborador y por área, '
             'utilizando metodologías probadas que favorezcan el crecimiento dentro '
             'de la empresa y la retroalimentación del desarrollo ocupacional.'),
            ('Fortalecer los otros dominios',
             'Capacitar a los colaboradores en la organización del tiempo y '
             'actividades; limitar el incremento en esta categoría o afectarla '
             'positivamente mediante estudios periódicos de tiempo y carga de trabajo.'),
        ],
    },
    'Jornada de trabajo e interferencia trabajo-familia': {
        'intro': (
            'Una adecuada gestión de la jornada laboral es esencial para garantizar '
            'la productividad y el bienestar de los trabajadores.'
        ),
        'bullets': [
            ('Implementación de horarios flexibles',
             'Permitir que los empleados ajusten su jornada laboral dentro de los '
             'límites establecidos, facilitando un mejor equilibrio entre sus '
             'responsabilidades personales y profesionales.'),
            ('Limitación de horas extras',
             'Restringir las horas de trabajo adicionales y asegurar que se respeten '
             'los periodos de descanso, evitando la fatiga acumulada y mejorando la '
             'seguridad en el trabajo.'),
            ('Rotación de turnos equitativa',
             'Establecer un sistema que alterne entre turnos diurnos y nocturnos de '
             'manera equitativa, garantizando que los empleados tengan tiempo '
             'suficiente para descansar.'),
            ('Distribución equitativa de la carga laboral',
             'Asegurar que las tareas sean distribuidas de manera justa entre todos '
             'los empleados, evitando la sobrecarga de trabajo en ciertos equipos '
             'o personas.'),
            ('Optimización de las pausas laborales',
             'Promover el uso eficiente de los descansos durante la jornada, '
             'asegurando que los trabajadores tengan tiempo adecuado para recuperarse '
             'y contribuyendo a su bienestar general.'),
            ('Fortalecer los otros dominios',
             'Respetar los tiempos de descanso y días no laborables; establecer '
             'espacios y políticas para la atención de asuntos personales en horario '
             'laboral; actualizar las políticas respecto a permisos para asuntos '
             'personales y/o emergencias.'),
        ],
    },
    'Liderazgo': {
        'intro': (
            'El liderazgo efectivo es un pilar fundamental del entorno organizacional. '
            'Desarrollar líderes competentes y empáticos reduce el ausentismo, '
            'mejora la cohesión de los equipos y eleva los indicadores de calidad.'
        ),
        'bullets': [
            ('Programa de desarrollo de habilidades directivas',
             'Diseñar e implementar talleres de liderazgo situacional, comunicación '
             'asertiva, gestión de conflictos y motivación de equipos dirigidos a '
             'todos los mandos medios y supervisores.'),
            ('Sesiones de retroalimentación periódica (one-on-one)',
             'Establecer reuniones individuales regulares entre supervisor y '
             'colaborador para revisar objetivos, reconocer logros y atender '
             'dificultades de manera oportuna.'),
            ('Diagnóstico del estilo de liderazgo por área',
             'Aplicar instrumentos de evaluación (360°) para identificar estilos de '
             'liderazgo y áreas de oportunidad en cada equipo, priorizando las '
             'intervenciones donde el impacto sea mayor.'),
            ('Fomento del liderazgo participativo',
             'Promover que los líderes involucren a su equipo en la toma de '
             'decisiones operativas, generando mayor compromiso y sentido '
             'de pertenencia.'),
            ('Mecanismo de reporte confidencial',
             'Crear o fortalecer un canal seguro para que los colaboradores reporten '
             'prácticas de liderazgo negativo, con procedimientos claros de atención '
             'y seguimiento sin represalias.'),
            ('Reconocimiento formal del desempeño de los líderes',
             'Incluir indicadores de clima organizacional y satisfacción del equipo '
             'dentro de los criterios de evaluación del desempeño de los supervisores '
             'y mandos medios.'),
        ],
    },
    'Relaciones en el trabajo': {
        'intro': (
            'Un clima de respeto y colaboración entre compañeros es determinante '
            'para la cohesión del equipo, la productividad y la retención del '
            'talento.'
        ),
        'bullets': [
            ('Talleres de comunicación y trabajo en equipo',
             'Implementar actividades formativas orientadas a fortalecer la '
             'comunicación horizontal, la colaboración y la resolución constructiva '
             'de conflictos entre compañeros.'),
            ('Actividades de integración y convivencia',
             'Organizar eventos periódicos de integración que favorezcan el '
             'conocimiento mutuo y el fortalecimiento de los vínculos entre '
             'los colaboradores de distintas áreas.'),
            ('Mecanismos de resolución de conflictos',
             'Establecer procedimientos formales y accesibles para la mediación y '
             'resolución de conflictos interpersonales, con personal capacitado '
             'para su atención.'),
            ('Política de respeto e inclusión',
             'Difundir y reforzar una política de respeto, no discriminación e '
             'inclusión en el trabajo, con sesiones de sensibilización dirigidas '
             'a todos los niveles.'),
            ('Canal de reporte de conductas inadecuadas',
             'Habilitar un mecanismo confidencial para reportar conductas de '
             'falta de respeto o conflictos interpersonales, con seguimiento '
             'documentado y tiempos de respuesta definidos.'),
        ],
    },
    'Violencia': {
        'intro': (
            'La prevención y atención de la violencia laboral es una obligación '
            'legal y ética de la organización, y su abordaje oportuno protege la '
            'salud mental y la dignidad de todos los colaboradores.'
        ),
        'bullets': [
            ('Difusión y actualización del protocolo de prevención de violencia laboral',
             'Asegurar que todos los colaboradores conozcan el protocolo de atención '
             'a violencia laboral, los canales de reporte y los derechos que les '
             'asisten, actualizándolo conforme a la normativa vigente.'),
            ('Capacitación en identificación y prevención de violencia',
             'Impartir talleres a todos los niveles jerárquicos sobre tipos de '
             'violencia laboral (física, psicológica, sexual), factores de riesgo '
             'y estrategias de prevención.'),
            ('Atención psicológica a personas afectadas',
             'Garantizar acceso a servicios de apoyo psicológico confidencial para '
             'colaboradores que hayan sido víctimas de violencia laboral, facilitando '
             'su recuperación y reincorporación.'),
            ('Investigación formal de casos reportados',
             'Establecer un procedimiento claro, justo y sin represalias para '
             'investigar y resolver los casos de violencia reportados, con '
             'documentación de resultados y seguimiento.'),
            ('Cultura de cero tolerancia',
             'Reforzar el mensaje institucional de cero tolerancia hacia cualquier '
             'forma de violencia laboral, con sanciones claras y comunicadas a '
             'todos los colaboradores.'),
        ],
    },
    'Reconocimiento del desempeño e inestabilidad': {
        'intro': (
            'El reconocimiento oportuno del desempeño y la percepción de estabilidad '
            'laboral son factores clave para el compromiso, la motivación y la '
            'retención del talento en la organización.'
        ),
        'bullets': [
            ('Sistema formal de reconocimiento del desempeño',
             'Diseñar e implementar un sistema de evaluación del desempeño que sea '
             'percibido como justo, transparente y que incluya reconocimientos '
             'tanto económicos como no económicos.'),
            ('Comunicación clara sobre la situación de la empresa',
             'Mantener una comunicación interna oportuna y honesta sobre los '
             'resultados, cambios organizacionales y perspectivas de la empresa, '
             'reduciendo la incertidumbre y los rumores.'),
            ('Plan de desarrollo y carrera',
             'Ofrecer a los colaboradores oportunidades de crecimiento profesional '
             'dentro de la organización, con rutas de carrera definidas y '
             'programas de desarrollo de competencias.'),
            ('Reconocimiento público de logros',
             'Establecer mecanismos de reconocimiento público (reuniones, '
             'tableros, comunicados) que visibilicen los logros individuales '
             'y colectivos.'),
            ('Encuestas de clima y seguimiento',
             'Aplicar encuestas periódicas de clima laboral para medir la '
             'percepción de reconocimiento y estabilidad, y actuar sobre los '
             'resultados con acciones concretas y comunicadas.'),
        ],
    },
    'Atención a clientes': {
        'intro': (
            'El personal que atiende clientes internos o externos está expuesto a '
            'demandas emocionales adicionales. La gestión adecuada de este dominio '
            'previene el desgaste profesional y mejora la calidad del servicio.'
        ),
        'bullets': [
            ('Capacitación en manejo de situaciones difíciles',
             'Brindar formación especializada en técnicas de comunicación asertiva, '
             'desescalada de conflictos y manejo del estrés en la interacción '
             'con clientes.'),
            ('Rotación de personal en puestos de alta exposición',
             'Implementar esquemas de rotación entre colaboradores que atienden '
             'clientes con mayor frecuencia o complejidad, previniendo el desgaste '
             'emocional acumulado.'),
            ('Apoyo psicológico para personal de atención',
             'Garantizar acceso a servicios de apoyo emocional y psicológico para '
             'colaboradores que enfrenten situaciones de alta tensión con clientes.'),
            ('Protocolos claros de atención y escalación',
             'Documentar y difundir procedimientos claros sobre cómo manejar '
             'quejas, reclamaciones y situaciones críticas con clientes, '
             'incluyendo rutas de escalación.'),
            ('Límites y protección frente a conductas agresivas',
             'Establecer políticas que protejan a los colaboradores de conductas '
             'agresivas por parte de clientes, con procedimientos de reporte '
             'y acompañamiento.'),
        ],
    },
    'Actitudes de supervisados': {
        'intro': (
            'Las actitudes de los colaboradores hacia sus supervisores influyen en '
            'la eficacia del liderazgo y en el clima del equipo. Abordar este '
            'dominio fortalece la confianza y la comunicación en ambos sentidos.'
        ),
        'bullets': [
            ('Espacios de retroalimentación ascendente',
             'Crear mecanismos formales (buzones, reuniones de equipo, encuestas) '
             'donde los colaboradores puedan expresar su percepción sobre el '
             'liderazgo y el funcionamiento del equipo de manera constructiva.'),
            ('Talleres de comunicación entre supervisores y equipos',
             'Facilitar sesiones conjuntas entre líderes y sus equipos para '
             'trabajar la comunicación, alinear expectativas y abordar conflictos '
             'de manera colaborativa.'),
            ('Clarificación de roles y expectativas',
             'Asegurar que todos los colaboradores tengan claridad sobre sus '
             'funciones, responsabilidades y lo que se espera de ellos, '
             'reduciendo fuentes de tensión con sus supervisores.'),
            ('Mediación en conflictos supervisor-colaborador',
             'Contar con un proceso de mediación formal para atender conflictos '
             'específicos entre supervisores y colaboradores, con apoyo de '
             'Recursos Humanos.'),
            ('Cultura de respeto mutuo en la jerarquía',
             'Reforzar los valores de respeto, profesionalismo y colaboración '
             'en la relación entre todos los niveles de la organización, '
             'independientemente del rol jerárquico.'),
        ],
    },
}

# Acciones generales de cumplimiento normativo (Informe Diagnóstico extendido,
# sección 11.1) — se listan siempre, sin depender del nivel de riesgo de
# ningún dominio en particular.
ACCIONES_GENERALES = [
    ('Establecer o actualizar la política de prevención de riesgos psicosociales',
     'Formular, documentar y difundir una política empresarial que declare el '
     'compromiso del patrón con la identificación, prevención y control de los '
     'factores de riesgo psicosocial y la violencia laboral, de conformidad con '
     'el Apartado 5.1 de la NOM-035-STPS-2018.'),
    ('Comunicar los resultados del diagnóstico a los trabajadores',
     'Presentar de manera accesible y comprensible los resultados de la '
     'evaluación a todos los colaboradores, garantizando transparencia y '
     'fomentando la participación activa en el diseño e implementación de las '
     'medidas de mejora.'),
    ('Implementar un programa de capacitación y sensibilización',
     'Diseñar e impartir talleres y cursos dirigidos a todos los niveles '
     'jerárquicos sobre identificación de factores de riesgo psicosocial, '
     'manejo del estrés, comunicación asertiva y prevención de la violencia '
     'laboral.'),
    ('Establecer mecanismos de atención a trabajadores',
     'Crear o fortalecer canales confidenciales para que los trabajadores '
     'puedan reportar situaciones de riesgo psicosocial o violencia laboral, '
     'con procedimientos claros de atención, seguimiento y resolución.'),
    ('Constituir o activar la Comisión de Seguridad e Higiene',
     'Asegurar el funcionamiento efectivo de la Comisión de Seguridad e '
     'Higiene, incorporando en su agenda el seguimiento de los factores de '
     'riesgo psicosocial identificados y las acciones correctivas '
     'correspondientes.'),
    ('Elaborar un plan de acción con metas y responsables',
     'Documentar un plan de intervención que establezca acciones específicas, '
     'plazos de implementación, indicadores de seguimiento y responsables '
     'designados para cada área de mejora identificada en el presente '
     'diagnóstico.'),
    ('Promover el equilibrio trabajo-familia',
     'Revisar la organización de las jornadas, horarios y cargas de trabajo '
     'para favorecer la conciliación entre la vida laboral y personal de los '
     'colaboradores, incluyendo políticas de flexibilidad donde sea '
     'operativamente viable.'),
    ('Fortalecer los canales de comunicación interna',
     'Implementar mecanismos efectivos de comunicación bidireccional entre la '
     'dirección, mandos medios y operativos, promoviendo la retroalimentación, '
     'la participación en la toma de decisiones y el reconocimiento del '
     'desempeño.'),
    ('Identificar y apoyar a trabajadores que requieran atención clínica',
     'Establecer un protocolo de detección y canalización de colaboradores que '
     'presenten indicadores de afectación a la salud mental derivados de la '
     'exposición a factores de riesgo psicosocial, brindando acceso a '
     'servicios de salud.'),
    ('Programar una reevaluación periódica',
     'Realizar una nueva aplicación de la Guía de Referencia III en un plazo '
     'no mayor a 12 meses, con el fin de evaluar la efectividad de las medidas '
     'implementadas y actualizar el diagnóstico de riesgo psicosocial del '
     'centro de trabajo.'),
]
