"""
Textos de interpretación clínico-organizacional para el reporte psicológico
NOM-035-STPS-2018 (DOF 23-oct-2018).

Fuente: definiciones del Apartado 4 y Guías de Referencia I, III y V de la norma.
Pendiente de visto bueno de psicólogos colaboradores antes de publicar en producción.

Se consumen como constantes en `documents/views.py` y se renderizan en
`documents/templates/documents/reporte_psicologico.html`.
"""

# ---------------------------------------------------------------------------
# Marco normativo y metodológico
# ---------------------------------------------------------------------------
MARCO_NORMATIVO = {
    'fundamento':
        'El presente reporte se elabora conforme a la Norma Oficial Mexicana '
        'NOM-035-STPS-2018, “Factores de riesgo psicosocial en el trabajo — '
        'Identificación, análisis y prevención”, publicada en el Diario Oficial '
        'de la Federación el 23 de octubre de 2018, con entrada en vigor de su '
        'segunda etapa el 23 de octubre de 2020.',
    'instrumentos': [
        ('Guía de Referencia I',
         'Identificación de los trabajadores que fueron sujetos a Acontecimientos '
         'Traumáticos Severos (ATS).'),
        ('Guía de Referencia III',
         'Identificación y análisis de los factores de riesgo psicosocial y '
         'evaluación del entorno organizacional. 72 reactivos en escala tipo '
         'Likert de frecuencia (0 = Nunca a 4 = Siempre), agrupados en 5 '
         'categorías y 14 dominios.'),
        ('Guía de Referencia V',
         'Datos del centro de trabajo y del trabajador: variables '
         'sociodemográficas y laborales.'),
    ],
    'criterio_guia_i':
        'Se considera caso positivo cuando el trabajador reporta al menos un (1) '
        'acontecimiento traumático severo (Sección I) y al menos dos (2) síntomas '
        'asociados de las Secciones II, III y IV (recuerdos persistentes, '
        'esfuerzo por evitar y afectación), conforme a la Guía de Referencia I.',
    'criterio_guia_iii':
        'La calificación de la Guía III se realiza por dominio y de forma global, '
        'comparando el puntaje obtenido contra los rangos normativos del cuadro '
        'oficial de puntajes, que define cinco niveles de riesgo: Nulo o '
        'despreciable, Bajo, Medio, Alto y Muy alto.',
}

# ---------------------------------------------------------------------------
# Guía I — Acontecimiento Traumático Severo
# ---------------------------------------------------------------------------
GUIA_I_DEFINICION = (
    'Acontecimiento Traumático Severo (Apartado 4.4 NOM-035): aquél que puede '
    'amenazar la vida o la integridad física de una persona o de varias, ante el '
    'que se experimenta miedo intenso, horror o sensación de desamparo, y que '
    'genera en quien lo vive o lo presencia una respuesta de estrés severa.'
)

GUIA_I_TEXTO_POSITIVO = (
    'El trabajador reporta haber sido expuesto a un acontecimiento traumático '
    'severo en el contexto laboral y presenta síntomas compatibles con una '
    'respuesta de estrés postraumático, incluyendo recuerdos intrusivos, conductas '
    'de evitación o alteraciones en el estado de alerta. Conforme al numeral 7.1 '
    'de la NOM-035-STPS-2018, el patrón está obligado a canalizar a este trabajador '
    'para recibir atención médica y, en su caso, psicológica. Este resultado no '
    'constituye un diagnóstico clínico; la evaluación individual por un psicólogo '
    'clínico o psiquiatra es indispensable para determinar la presencia o ausencia '
    'de Trastorno de Estrés Postraumático (TEPT) u otras condiciones asociadas.'
)

GUIA_I_TEXTO_SIN_INDICADORES = (
    'Los trabajadores evaluados no reportan exposición a acontecimientos '
    'traumáticos severos o, habiéndola reportado, no presentan síntomas asociados '
    'que alcancen el umbral de atención establecido por la norma. No se requiere '
    'canalización inmediata por este instrumento.'
)

# ---------------------------------------------------------------------------
# Guía III — Interpretación por nivel de riesgo global
# ---------------------------------------------------------------------------
NIVEL_GLOBAL = {
    'nulo':
        'La organización presenta una exposición nula o despreciable a factores de '
        'riesgo psicosocial en el trabajo. Las condiciones laborales evaluadas no '
        'representan una fuente de daño a la salud mental de los trabajadores en el '
        'ciclo evaluado. Se recomienda mantener las prácticas actuales y aplicar el '
        'cuestionario en el siguiente ciclo normativo para verificar continuidad.',
    'bajo':
        'Se detecta una exposición baja a factores de riesgo psicosocial. Aunque no '
        'representa un riesgo inmediato, existen áreas de mejora que, de no atenderse, '
        'pueden escalar en ciclos posteriores. El patrón debe implementar acciones '
        'preventivas enfocadas en los dominios con mayor puntaje, reforzar la '
        'comunicación interna y revisar las condiciones identificadas en la siguiente '
        'evaluación anual.',
    'medio':
        'Se detecta una exposición media a factores de riesgo psicosocial. Este nivel '
        'indica que las condiciones de trabajo están generando tensión psicológica que '
        'puede afectar el bienestar, la satisfacción laboral y la productividad de los '
        'trabajadores. Conforme al Apartado 8 de la NOM-035-STPS-2018, el patrón debe '
        'elaborar un plan de acción con medidas concretas, plazos definidos y '
        'responsables asignados, orientadas a reducir los factores identificados como '
        'prioritarios.',
    'alto':
        'Se detecta una exposición alta a factores de riesgo psicosocial. Las '
        'condiciones laborales evaluadas representan una amenaza significativa para la '
        'salud mental y física de los trabajadores, con riesgo de provocar o agravar '
        'trastornos de ansiedad, depresión, agotamiento laboral (burnout) y trastornos '
        'musculoesqueléticos de origen psicosocial. Se requieren acciones inmediatas: '
        'intervención organizacional en los dominios críticos, seguimiento mensual del '
        'plan de acción, y evaluación individual de los trabajadores con puntajes más '
        'elevados. El patrón debe notificar a la Comisión de Seguridad e Higiene y '
        'registrar las acciones en el programa de seguridad y salud en el trabajo.',
    'muy_alto':
        'Se detecta una exposición muy alta a factores de riesgo psicosocial. Este '
        'nivel constituye una situación crítica que requiere intervención urgente. La '
        'norma establece que el patrón debe adoptar de inmediato medidas para controlar '
        'los factores identificados, ofrecer atención médica y psicológica colectiva e '
        'individual, y elaborar un programa de intervención con indicadores de '
        'seguimiento. La persistencia de este nivel de exposición sin intervención '
        'puede derivar en daños severos y permanentes a la salud de los trabajadores, '
        'así como en responsabilidades legales para la organización conforme a la Ley '
        'Federal del Trabajo.',
}

# ---------------------------------------------------------------------------
# Guía III — Interpretación por dominio
# Cada entrada: 'mide' (qué evalúa) y 'alto' (texto clínico para nivel Alto/Muy Alto)
# ---------------------------------------------------------------------------
DOMINIO_INTERPRETACION = {
    'D1': {
        'mide':
            'Presencia de condiciones físicas y materiales del entorno laboral que '
            'pueden representar un riesgo para la seguridad o la comodidad del '
            'trabajador: espacio, higiene, seguridad percibida, exposición a riesgos '
            'físicos y peligrosidad de las actividades.',
        'alto':
            'Los trabajadores perciben que su entorno físico de trabajo representa un '
            'riesgo para su integridad o salud. La exposición prolongada a condiciones '
            'ambientales adversas activa de forma crónica el sistema de respuesta al '
            'estrés, incrementando el riesgo de trastornos de ansiedad, insomnio y '
            'patologías musculoesqueléticas. Se recomienda realizar una evaluación de '
            'riesgos físicos del centro de trabajo, corregir las condiciones inseguras '
            'identificadas y comunicar a los trabajadores las medidas adoptadas para '
            'reducir la percepción de peligro.',
    },
    'D2': {
        'mide':
            'Exigencias de velocidad en la ejecución de tareas: trabajar sin parar, '
            'quedarse tiempo adicional y mantener un ritmo acelerado de forma habitual.',
        'alto':
            'El ritmo de trabajo impuesto supera la capacidad de recuperación '
            'fisiológica y psicológica del trabajador. La bibliografía científica '
            'vincula el ritmo excesivo con agotamiento laboral (burnout), fatiga '
            'crónica, errores operativos y accidentes. Se recomienda revisar la carga '
            'de trabajo asignada, establecer pausas activas reglamentadas y redistribuir '
            'tareas en periodos de alta demanda.',
    },
    'D3': {
        'mide':
            'Demandas cognitivas del puesto: concentración sostenida, memorización de '
            'información abundante, toma de decisiones bajo presión y atención simultánea '
            'a múltiples tareas.',
        'alto':
            'Las demandas cognitivas del puesto exceden los recursos atencionales del '
            'trabajador de forma habitual. La sobrecarga mental sostenida está asociada '
            'a deterioro de la función ejecutiva, aumento de errores, fatiga mental, '
            'trastornos del sueño e incremento del riesgo de trastornos ansiosos. Se '
            'recomienda revisar el diseño del puesto, reducir la multitarea forzada, y '
            'proveer herramientas o apoyos tecnológicos que reduzcan la carga cognitiva '
            'innecesaria.',
    },
    'D4': {
        'mide':
            'Ambigüedad y conflicto de rol: recibir instrucciones contradictorias, '
            'realizar actividades percibidas como innecesarias, y asumir '
            'responsabilidades sobre resultados de otras personas.',
        'alto':
            'El trabajador experimenta ambigüedad y conflicto de rol de forma crónica. '
            'La falta de claridad sobre las responsabilidades propias y la percepción de '
            'contradicción en las instrucciones recibidas generan tensión psicológica '
            'constante, reducen el sentido de eficacia personal y se asocian a mayor '
            'incidencia de ansiedad y síntomas depresivos. Se recomienda revisar y '
            'comunicar con claridad las descripciones de puesto, establecer canales '
            'únicos de instrucción y eliminar duplicidad de mandos.',
    },
    'D5': {
        'mide':
            'Extensión y gestión del tiempo de trabajo: horas extras frecuentes, trabajo '
            'en días de descanso o festivos, y conflicto entre el tiempo dedicado al '
            'trabajo y las responsabilidades familiares o personales.',
        'alto':
            'La jornada de trabajo está interfiriendo significativamente con la vida '
            'personal y familiar del trabajador, configurando un conflicto '
            'trabajo-familia de alta intensidad. Este factor es uno de los predictores '
            'más robustos de agotamiento emocional, deterioro de la salud cardiovascular '
            'y trastornos del sueño en la literatura de salud ocupacional. Se recomienda '
            'auditar las horas extra reales trabajadas, implementar políticas de '
            'desconexión digital fuera del horario laboral y revisar la dotación de '
            'personal en las áreas con mayor reporte de sobrecarga.',
    },
    'D6': {
        'mide':
            'Grado de control del trabajador sobre su propio ritmo, método y '
            'organización de tareas, así como su capacidad de desarrollo y aspiración '
            'profesional dentro del centro de trabajo.',
        'alto':
            'Los trabajadores perciben un bajo control sobre su trabajo, lo que según el '
            'modelo Demanda-Control de Karasek constituye la combinación de mayor riesgo '
            'para la salud cardiovascular y mental. La autonomía insuficiente limita la '
            'sensación de competencia, reduce la motivación intrínseca y se asocia a '
            'mayor probabilidad de desarrollar depresión laboral. Se recomienda revisar '
            'el diseño de puestos para incorporar márgenes razonables de autonomía, '
            'establecer metas de desarrollo profesional y socializar con los trabajadores '
            'las oportunidades de crecimiento existentes en la organización.',
    },
    'D7': {
        'mide':
            'Frecuencia e impacto de los cambios organizacionales sobre la labor del '
            'trabajador, y el grado en que sus ideas son tomadas en cuenta ante dichos '
            'cambios.',
        'alto':
            'Los trabajadores perciben que los cambios organizacionales los afectan '
            'negativamente y que sus aportaciones no son consideradas. La incertidumbre '
            'ante el cambio sin participación activa activa el sistema de amenaza y '
            'genera respuestas de estrés crónico. Se recomienda implementar procesos de '
            'comunicación transparente ante reestructuraciones, incluir a los '
            'trabajadores afectados en el diseño de los cambios y proveer acompañamiento '
            'durante las transiciones.',
    },
    'D8': {
        'mide':
            'Claridad en las funciones y objetivos del puesto, acceso a capacitación '
            'útil y pertinente, y disponibilidad de información para resolver problemas '
            'laborales.',
        'alto':
            'Los trabajadores reportan déficit de capacitación y de información para el '
            'desempeño de su puesto. La falta de habilidades percibidas para afrontar '
            'las demandas del trabajo es un factor de riesgo conocido para el desarrollo '
            'de estrés laboral crónico y síndrome de agotamiento. Se recomienda realizar '
            'un diagnóstico de necesidades de capacitación, implementar un programa de '
            'inducción y formación continua, y asegurar que los trabajadores cuenten con '
            'acceso oportuno a la información necesaria para su función.',
    },
    'D9': {
        'mide':
            'Calidad de la relación con el jefe inmediato: apoyo para organizar el '
            'trabajo, comunicación oportuna, valoración de las opiniones del trabajador '
            'y orientación para la resolución de problemas.',
        'alto':
            'La relación con el liderazgo inmediato es percibida como deficiente en '
            'apoyo, comunicación y reconocimiento. El liderazgo de baja calidad es uno '
            'de los factores de riesgo psicosocial con mayor impacto documentado sobre '
            'la salud mental de los equipos de trabajo, asociado a mayor prevalencia de '
            'burnout, rotación de personal y ausentismo. Se recomienda implementar un '
            'programa de desarrollo de habilidades de liderazgo para mandos medios y '
            'superiores, con énfasis en comunicación efectiva, retroalimentación '
            'constructiva y gestión del clima laboral.',
    },
    'D10': {
        'mide':
            'Calidad del vínculo con los pares: confianza, resolución respetuosa de '
            'conflictos, sentido de pertenencia, colaboración y apoyo entre compañeros.',
        'alto':
            'El ambiente de relaciones interpersonales entre compañeros es percibido '
            'como deteriorado. Las relaciones laborales de baja calidad reducen el apoyo '
            'social percibido, que es uno de los amortiguadores más importantes frente '
            'al estrés laboral. Su deterioro se asocia a mayor aislamiento, conflictos '
            'interpersonales, conductas de exclusión y mayor vulnerabilidad individual a '
            'trastornos del estado de ánimo. Se recomienda implementar actividades de '
            'integración de equipos, establecer protocolos claros de resolución de '
            'conflictos y revisar si existen situaciones de hostigamiento no reportadas '
            'formalmente.',
    },
    'D11': {
        'mide':
            'Percepción de justicia en la evaluación del desempeño, oportunidades de '
            'crecimiento, pago puntual y justo, reconocimiento por resultados, '
            'estabilidad del empleo y orgullo/compromiso organizacional.',
        'alto':
            'Los trabajadores perciben que su desempeño no es reconocido de forma justa, '
            'que las oportunidades de crecimiento son limitadas y que la estabilidad de '
            'su empleo es incierta. La percepción de injusticia organizacional es un '
            'predictor robusto de síntomas depresivos, agotamiento emocional y conductas '
            'contraproducentes. Se recomienda revisar los sistemas de evaluación de '
            'desempeño para asegurar su transparencia y equidad, comunicar con claridad '
            'las políticas de compensación y crecimiento, y reforzar acciones de '
            'reconocimiento formal e informal.',
    },
    'D12': {
        'mide':
            'Exposición a actos de violencia psicológica en el trabajo: críticas '
            'destructivas, burlas, humillaciones, exclusión deliberada, manipulación, '
            'apropiación de logros ajenos, bloqueo de ascensos y presencia de violencia '
            'en el entorno laboral.',
        'alto':
            'Se detecta una exposición significativa a actos de violencia psicológica en '
            'el trabajo. La violencia laboral de tipo psicológico —también denominada '
            'mobbing o acoso laboral— produce daños severos y progresivos en la salud '
            'mental del trabajador: ansiedad, depresión, trastorno de estrés '
            'postraumático, baja autoestima y deterioro de la identidad profesional. '
            'Conforme al numeral 7 de la NOM-035-STPS-2018, el patrón tiene la obligación '
            'de establecer y difundir una política de prevención de violencia laboral, '
            'así como adoptar medidas para prevenir y atender las prácticas opuestas al '
            'entorno organizacional favorable. Se recomienda activar de forma inmediata '
            'el protocolo de atención a casos de violencia, garantizar la '
            'confidencialidad de los reportes y proveer acompañamiento psicológico a las '
            'personas afectadas.',
    },
    'D13': {
        'mide':
            'Exigencias emocionales específicas de los puestos que implican trato '
            'directo con clientes o usuarios: atender personas enojadas, en situación de '
            'vulnerabilidad o de violencia, y la necesidad de gestionar emociones propias '
            'en beneficio del servicio (trabajo emocional).',
        'alto':
            'Los trabajadores en contacto directo con clientes están experimentando una '
            'carga emocional elevada derivada de su trabajo. La supresión crónica de '
            'emociones propias para mantener la actitud de servicio requerida (trabajo '
            'emocional de superficie) es un factor de riesgo específico para el '
            'agotamiento emocional y el síndrome de burnout, especialmente en servicios '
            'de salud, atención a personas vulnerables y puestos de atención a clientes '
            'conflictivos. Se recomienda implementar supervisión psicológica periódica '
            'para estos puestos, establecer protocolos de desescalada ante situaciones '
            'de violencia con clientes y proveer espacios de recuperación emocional entre '
            'turnos de atención.',
    },
    'D14': {
        'mide':
            'Dificultades específicas que enfrentan los supervisores derivadas de las '
            'actitudes de sus subordinados: falta de comunicación oportuna, '
            'obstaculización de resultados, poca cooperación e ignorancia de sugerencias '
            'de mejora.',
        'alto':
            'Los supervisores y jefes de área reportan dificultades significativas '
            'relacionadas con las actitudes de las personas que supervisan. Esta '
            'situación genera en el supervisor una tensión de rol específica: la '
            'responsabilidad sobre resultados que dependen de terceros, combinada con la '
            'percepción de falta de control sobre el desempeño del equipo, incrementa el '
            'riesgo de agotamiento laboral en mandos medios. Se recomienda revisar los '
            'procesos de comunicación ascendente y descendente en los equipos, '
            'identificar si las actitudes reportadas tienen origen en problemas de clima '
            'organizacional más amplios, y proveer a los supervisores herramientas de '
            'gestión de equipos y resolución de conflictos.',
    },
}

# Texto estándar de la sección de limitaciones del estudio
LIMITACIONES = (
    'Los resultados presentados reflejan la percepción de los trabajadores respecto '
    'a sus condiciones de trabajo durante el periodo evaluado y no constituyen un '
    'diagnóstico clínico individual. La identificación de factores de riesgo '
    'psicosocial mediante las Guías de Referencia de la NOM-035-STPS-2018 tiene una '
    'finalidad preventiva y organizacional; los casos que requieren atención '
    'especializada deben ser confirmados mediante evaluación clínica individual por '
    'un profesional de la salud mental. La validez de las conclusiones depende de la '
    'tasa de respuesta obtenida y de la veracidad con que los trabajadores '
    'respondieron los instrumentos. Los resultados deben interpretarse en el contexto '
    'organizacional específico del centro de trabajo.'
)
