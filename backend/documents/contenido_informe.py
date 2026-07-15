"""Contenido estático del Informe Diagnóstico DOCX (formato aprobado por
dirección, jul-2026). SOLO lo consume `build_informe_diagnostico_docx`;
el flujo borrador/reporte psicológico sigue usando contenido_normativo.py.

Los bloques BLOQUE_* fueron extraídos textualmente del documento de
referencia (espacios finales, tabs y saltos internos incluidos): cada
ítem es un párrafo con su estilo Word, alineación y segmentos
(texto, negrita).
"""

BLOQUE_METODOLOGIA_PROC = [
    {
        'style': 'Intense Quote',
        'align': None,
        'segs': [
            ('Antes de la aplicación:', False),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('Se determinó el número mínimo de trabajadores a quienes se aplicarían los cuestionarios, el cual debía ser igual o superior al tamaño de muestra calculado mediante la Ecuación 1 de la NOM-035-STPS-2018. ', False),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('A partir de la plantilla nominal de trabajadores activos del centro de trabajo, con fecha de corte previamente definida, se realizó una selección aleatoria estratificada. Se procuró que todos los trabajadores elegibles tuvieran posibilidad de ser seleccionados y que la distribución de hombres y mujeres correspondiera a su proporción en la población del centro de trabajo. La estratificación complementaria consideró las áreas, turnos y tipos de puesto establecidos para el estudio. ', False),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('Las personas que permanecieron imposibilitadas para participar durante todo el periodo de aplicación, por baja, licencia, incapacidad temporal o ausencia justificada, fueron registradas como no disponibles. Cuando fue necesario realizar una sustitución, ésta se efectuó aleatoriamente con una persona del mismo estrato, dejando evidencia del motivo y del procedimiento aplicado. ', False),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('Se verificó que las condiciones de las instalaciones, el mobiliario y los equipos utilizados fueran adecuadas. ', False),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('Se realizó la presentación del aplicador ante las personas participantes. ', False),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('Se explicó el objetivo de la evaluación. ', False),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('Se enfatizó la protección de la privacidad y confidencialidad de la información, señalando que las respuestas y resultados serían utilizados exclusivamente para la identificación, prevención y atención de las condiciones relacionadas con el ambiente de trabajo. ', False),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('Se proporcionaron instrucciones claras sobre la forma de responder las diferentes secciones. Se indicó que el cuestionario debía contestarse completamente, que no existían respuestas correctas o incorrectas, que era necesario mantener la concentración y que las respuestas debían considerar las condiciones de los dos últimos meses y expresar la opinión del trabajador con sinceridad. ', False),
        ],
    },
    {
        'style': 'Intense Quote',
        'align': None,
        'segs': [
            ('Durante la aplicación del cuestionario:', False),
        ],
    },
    {
        'style': 'List Number',
        'align': None,
        'segs': [
            ('Se propició un ambiente de respeto y confianza. ', False),
        ],
    },
    {
        'style': 'List Number',
        'align': None,
        'segs': [
            ('Se permitió una comunicación fluida entre los trabajadores y el personal aplicador. ', False),
        ],
    },
    {
        'style': 'List Number',
        'align': None,
        'segs': [
            ('Se aclararon dudas sobre el funcionamiento del instrumento, sin explicar, interpretar o sugerir el sentido de las respuestas. ', False),
        ],
    },
    {
        'style': 'List Number',
        'align': None,
        'segs': [
            ('Se presentó la plataforma digital y el procedimiento para ingresar, responder, avanzar y concluir cada cuestionario y sus secciones. ', False),
        ],
    },
    {
        'style': 'List Number',
        'align': None,
        'segs': [
            ('Se verificó que las indicaciones hubieran quedado claras. ', False),
        ],
    },
    {
        'style': 'List Number',
        'align': None,
        'segs': [
            ('Se evitó interrumpir a los trabajadores mientras respondían. ', False),
        ],
    },
    {
        'style': 'List Number',
        'align': None,
        'segs': [
            ('Se evitó conducir, persuadir o dirigir las respuestas.', False),
        ],
    },
    {
        'style': 'Intense Quote',
        'align': None,
        'segs': [
            ('Después de la aplicación del cuestionario:', False),
        ],
    },
    {
        'style': 'List Number',
        'align': 'JUSTIFY',
        'segs': [
            ('Al concluir los instrumentos, la plataforma realizó una verificación automática de completitud y mostró al trabajador una confirmación de envío. El coordinador de la sesión verificó únicamente el estado de finalización o el folio de confirmación, sin visualizar las respuestas individuales. ', False),
        ],
    },
    {
        'style': 'List Number',
        'align': 'JUSTIFY',
        'segs': [
            ('Se conciliaron los registros de personas convocadas, aplicaciones iniciadas, aplicaciones completadas, cuestionarios excluidos, cuestionarios válidos y cuestionarios finalmente analizados. Se comprobó que el número de cuestionarios válidos fuera igual o superior al tamaño mínimo de muestra requerido. ', False),
        ],
    },
    {
        'style': 'List Number',
        'align': 'JUSTIFY',
        'segs': [
            ('Para fines operativos, los instrumentos se aplicaron en el orden siguiente: ', False),
        ],
    },
    {
        'style': 'List Number',
        'align': 'JUSTIFY',
        'segs': [
            ('a)', True),
            (' Guía de Referencia III: Identificación y análisis de los factores de riesgo psicosocial y evaluación del entorno organizacional.\n', False),
            ('b)', True),
            (' Guía de Referencia I: Identificación de trabajadores sujetos a acontecimientos traumáticos severos.\n', False),
            ('c)', True),
            (' Guía de Referencia V: Datos del trabajador.', False),
        ],
    },
    {
        'style': 'List Number',
        'align': 'JUSTIFY',
        'segs': [
        ],
    },
    {
        'style': 'Heading 3',
        'align': 'JUSTIFY',
        'segs': [
            ('6.4. Procesamiento a digital', False),
        ],
    },
    {
        'style': 'Normal',
        'align': 'JUSTIFY',
        'segs': [
            ('Para la identificación y análisis de los factores de riesgo psicosocial y la evaluación del entorno organizacional se utilizó el cuestionario de la Guía de Referencia III, el cual contempla la forma de aplicación, el procedimiento de calificación y los niveles de riesgo previstos en el numeral 7.4 de la NOM-035-STPS-2018. De manera complementaria, se aplicó la Guía de Referencia I para identificar y canalizar a los trabajadores sujetos a acontecimientos traumáticos severos, de conformidad con el numeral 5.5 y el apartado GR.I de dicha guía. Al utilizarse los instrumentos de referencia de la propia NOM, no se empleó un cuestionario alternativo sujeto al procedimiento de validación señalado en el numeral 7.5.\t', False),
        ],
    },
    {
        'style': 'Normal',
        'align': 'JUSTIFY',
        'segs': [
        ],
    },
    {
        'style': 'Normal',
        'align': 'JUSTIFY',
        'segs': [
            ('Captura y validación de respuestas', True),
        ],
    },
    {
        'style': 'Normal',
        'align': 'JUSTIFY',
        'segs': [
            ('Los cuestionarios fueron respondidos directamente por cada trabajador mediante una plataforma digital. El sistema registró las respuestas y verificó:', False),
        ],
    },
    {
        'style': 'Normal',
        'align': 'JUSTIFY',
        'segs': [
            ('Presencia de todos los reactivos obligatorios. ', False),
        ],
    },
    {
        'style': 'Normal',
        'align': 'JUSTIFY',
        'segs': [
            ('Valores dentro del rango permitido. ', False),
        ],
    },
    {
        'style': 'Normal',
        'align': 'JUSTIFY',
        'segs': [
            ('Integridad de las preguntas filtro. ', False),
        ],
    },
    {
        'style': 'Normal',
        'align': 'JUSTIFY',
        'segs': [
            ('Consistencia de los reactivos condicionados. ', False),
        ],
    },
    {
        'style': 'Normal',
        'align': 'JUSTIFY',
        'segs': [
            ('Ausencia de duplicidades. ', False),
        ],
    },
    {
        'style': 'Normal',
        'align': 'JUSTIFY',
        'segs': [
            ('Correspondencia entre trabajador, centro de trabajo, ciclo y versión del cuestionario. ', False),
        ],
    },
    {
        'style': 'Normal',
        'align': 'JUSTIFY',
        'segs': [
            ('El estado “completado” indicó que la persona concluyó el cuestionario; posteriormente, el sistema aplicó las reglas de validación. Únicamente los cuestionarios completados y validados fueron incluidos en el análisis. Los registros parciales, inconsistentes o inválidos se conservaron para trazabilidad, pero fueron excluidos de los cálculos finales.', False),
        ],
    },
    {
        'style': 'Normal',
        'align': 'JUSTIFY',
        'segs': [
            ('Identificación y confidencialidad', True),
        ],
    },
    {
        'style': 'Normal',
        'align': 'JUSTIFY',
        'segs': [
            ('Cada trabajador fue vinculado mediante un folio o número de empleado. Este mecanismo permitió relacionar las aplicaciones y dar seguimiento a los casos autorizados, sin incluir identificadores personales en el informe general. La base individual se mantuvo con acceso restringido, mientras que los resultados del informe se presentaron de manera agregada. Los datos individuales relacionados con ATS o seguimiento clínico se reservaron para un anexo confidencial separado.', False),
        ],
    },
    {
        'style': 'Normal',
        'align': 'JUSTIFY',
        'segs': [
            ('Cálculo de resultados de la Guía I', True),
        ],
    },
    {
        'style': 'Normal',
        'align': 'JUSTIFY',
        'segs': [
            ('El sistema identificó si el trabajador respondió afirmativamente a al menos uno de los acontecimientos incluidos en la Sección I. Cuando todas las respuestas fueron negativas, las secciones posteriores se consideraron no aplicables.', False),
        ],
    },
    {
        'style': 'Normal',
        'align': 'JUSTIFY',
        'segs': [
            ('Cuando existió al menos una respuesta afirmativa en la Sección I, se verificaron independientemente los criterios siguientes:', False),
        ],
    },
    {
        'style': 'Normal',
        'align': 'JUSTIFY',
        'segs': [
            ('Una o más respuestas afirmativas en la Sección II. ', False),
        ],
    },
    {
        'style': 'Normal',
        'align': 'JUSTIFY',
        'segs': [
            ('Tres o más respuestas afirmativas en la Sección III. ', False),
        ],
    },
    {
        'style': 'Normal',
        'align': 'JUSTIFY',
        'segs': [
            ('Dos o más respuestas afirmativas en la Sección IV. ', False),
        ],
    },
    {
        'style': 'Normal',
        'align': 'JUSTIFY',
        'segs': [
            ('El cumplimiento de cualquiera de estos criterios determinó que el trabajador debía ser canalizado para atención clínica. Este resultado constituye un criterio de detección y canalización y no un diagnóstico clínico. ', False),
        ],
    },
    {
        'style': 'Normal',
        'align': 'JUSTIFY',
        'segs': [
            ('Cálculo de resultados de la Guía III', True),
        ],
    },
    {
        'style': 'Normal',
        'align': 'JUSTIFY',
        'segs': [
            ('La Guía III contiene 72 reactivos potencialmente aplicables. Para cada cuestionario, las respuestas fueron transformadas en puntajes conforme a las dos direcciones de calificación de la Tabla 5. Posteriormente:', False),
        ],
    },
    {
        'style': 'Normal',
        'align': 'JUSTIFY',
        'segs': [
            ('Cdom se obtuvo sumando los puntajes de los reactivos que integran cada dominio. ', False),
        ],
    },
    {
        'style': 'Normal',
        'align': 'JUSTIFY',
        'segs': [
            ('Ccat se obtuvo sumando los puntajes de los reactivos que integran cada categoría. ', False),
        ],
    },
    {
        'style': 'Normal',
        'align': 'JUSTIFY',
        'segs': [
            ('Cfinal se obtuvo sumando los puntajes de todos los reactivos aplicables del cuestionario. ', False),
        ],
    },
    {
        'style': 'Normal',
        'align': 'JUSTIFY',
        'segs': [
            ('La agrupación se realizó conforme a la Tabla 6. ', False),
        ],
    },
    {
        'style': 'Normal',
        'align': 'JUSTIFY',
        'segs': [
            ('Los reactivos 65–68 sólo se incluyeron cuando el trabajador indicó que atendía clientes, usuarios o personas. Los reactivos 69–72 sólo se incluyeron cuando indicó que supervisaba a otros trabajadores. Cuando el filtro fue negativo, esos reactivos se consideraron no aplicables y no se sustituyeron por cero. Cuando el filtro fue afirmativo y existieron respuestas faltantes, el cuestionario fue marcado para revisión o exclusión.', False),
        ],
    },
    {
        'style': 'Normal',
        'align': 'JUSTIFY',
        'segs': [
            ('Los niveles de riesgo se determinaron mediante los puntos de corte oficiales de la calificación final, de las cinco categorías y de los diez dominios. Los puntos de corte se aplicaron a cada cuestionario individual y no a promedios organizacionales.', False),
        ],
    },
    {
        'style': 'Normal',
        'align': 'JUSTIFY',
        'segs': [
            ('6.5. Evaluación y análisis de resultados', True),
        ],
    },
    {
        'style': 'Normal',
        'align': 'JUSTIFY',
        'segs': [
            ('La evaluación se realizó únicamente con cuestionarios completados y validados. Para cada trabajador se calcularon la calificación final, las cinco categorías y los diez dominios oficiales, y se determinó el nivel correspondiente conforme a los puntos de corte de la Guía III.', False),
        ],
    },
    {
        'style': 'Normal',
        'align': 'JUSTIFY',
        'segs': [
            ('A nivel del centro de trabajo, los resultados se analizaron mediante la distribución de cuestionarios individuales en los niveles Nulo o despreciable, Bajo, Medio, Alto y Muy alto. También se calcularon los porcentajes ubicados en nivel Medio o superior y en nivel Alto o Muy alto. No se asignó un nivel oficial único al centro de trabajo mediante el promedio, la mediana o la moda; estos estadísticos, cuando se muestran, tienen exclusivamente una función descriptiva. La Guía III determina el nivel a partir del resultado de cada cuestionario. ', False),
        ],
    },
    {
        'style': 'Normal',
        'align': 'JUSTIFY',
        'segs': [
            ('Las dimensiones se analizaron mediante puntajes y porcentajes descriptivos respecto de su máximo posible. Debido a que la NOM no establece puntos de corte por dimensión, no se les asignaron niveles oficiales de riesgo.', False),
        ],
    },
    {
        'style': 'Normal',
        'align': 'JUSTIFY',
        'segs': [
            ('Los resultados se desagregaron por área únicamente cuando el número de cuestionarios válidos permitió conservar la confidencialidad. Las conclusiones se formularon a partir de los hallazgos observados y sirvieron para priorizar las acciones preventivas, las medidas de control y el Programa de intervención previsto para los niveles Medio, Alto y Muy alto. ', False),
        ],
    },
    {
        'style': 'Normal',
        'align': 'JUSTIFY',
        'segs': [
        ],
    },
]

BLOQUE_ATS_INTRO = [
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('De acuerdo con el numeral ', False),
            ('4.1 de la NOM-035-STPS-2018', True),
            (', un acontecimiento traumático severo es aquel experimentado durante o con motivo del trabajo, caracterizado por la ocurrencia de la muerte o por representar un peligro real para la integridad física de una o varias personas, y que puede generar trastorno de estrés postraumático en quien lo sufre o lo presencia. Entre los ejemplos señalados por la norma se encuentran explosiones, derrumbes, incendios de gran magnitud, accidentes graves o mortales, asaltos con violencia, secuestros y homicidios. ', False),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('La Guía de Referencia I permite identificar a los trabajadores que reportaron haber experimentado o presenciado un acontecimiento de esta naturaleza y que, además, presentan respuestas relacionadas con recuerdos persistentes, evitación o afectación posterior al evento. El cumplimiento de estos criterios constituye un indicador para la canalización y atención correspondiente; no representa por sí mismo un diagnóstico clínico de trastorno de estrés postraumático ni de otra condición de salud mental.', False),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('Conforme al numeral ', False),
            ('5.5 de la NOM-035-STPS-2018', True),
            (', el patrón deberá identificar a los trabajadores que fueron sujetos a acontecimientos traumáticos severos durante o con motivo del trabajo y canalizarlos para su atención a la institución de seguridad social o privada, o al médico del centro de trabajo o de la empresa. La instancia de salud correspondiente determinará, en su caso, la necesidad de evaluación médica, psicológica o psiquiátrica especializada. ', False),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('Criterio de la Guía de Referencia I', True),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('Se considera que una persona cumple el criterio para canalización cuando presenta:', False),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('al menos una respuesta afirmativa en la ', False),
            ('Sección I', True),
            (', y ', False),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('además, cualquiera de las condiciones siguientes: ', False),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('una o más respuestas afirmativas en la ', False),
            ('Sección II', True),
            ('; ', False),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('tres o más respuestas afirmativas en la ', False),
            ('Sección III', True),
            ('; ', False),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('dos o más respuestas afirmativas en la ', False),
            ('Sección IV', True),
            ('. ', False),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('Los criterios de las secciones II, III y IV se evalúan de manera independiente; no deben sumarse entre sí para formar un único punto de corte.', False),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
        ],
    },
]

BLOQUE_RESPONSABLES = [
    {
        'style': 'Normal',
        'align': None,
        'segs': [
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('12. Responsables de la implementación y seguimiento', True),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('La implementación de las medidas de prevención, control e intervención derivadas de los resultados de la evaluación deberá realizarse de manera coordinada entre los responsables técnicos externos y las áreas internas del centro de trabajo. Las acciones deberán integrarse al Programa de intervención, asignando responsables, plazos, indicadores, metas y evidencias de cumplimiento.', False),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('La responsabilidad del cumplimiento de la NOM-035-STPS-2018 corresponde al patrón y a los representantes designados por el centro de trabajo. La participación de los consultores externos tiene carácter técnico, metodológico y de acompañamiento, sin sustituir las obligaciones legales y operativas de la organización.', False),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('12.1. Coordinación técnica y metodológica', True),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('Carlos Alberto González Becerra', True),
            ('\nCapacitador Externo registrado ante la Secretaría del Trabajo y Previsión Social\nRegistro: ', False),
            ('IAI-17117Q25-026', True),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('Responsabilidades:', False),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('Coordinar técnicamente la interpretación de los resultados. ', False),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('Verificar que las acciones propuestas sean congruentes con los hallazgos de la Guía de Referencia I y la Guía de Referencia III. ', False),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('Asesorar en la integración del Programa de intervención. ', False),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('Proponer indicadores para el seguimiento de las acciones preventivas y correctivas. ', False),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('Orientar la revisión de la política de prevención de riesgos psicosociales. ', False),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('Dar acompañamiento técnico en la difusión de resultados y campañas de sensibilización. ', False),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('Verificar la congruencia metodológica de los informes, matrices de intervención y evidencias documentales. ', False),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('Participar en la revisión del avance y efectividad de las medidas implementadas. ', False),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('12.2. Consultoría en el análisis de resultados y recomendaciones operativas y organizacionales', True),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('Ing. Luis Olivares', True),
            ('\nConsultor en mejora organizacional y operativa', False),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('Responsabilidades:', False),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('Traducir los resultados de categorías, dominios y áreas prioritarias en acciones aplicables a la operación. ', False),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('Formular recomendaciones específicas para las áreas de producción, operaciones, calidad, mantenimiento, logística y áreas administrativas. ', False),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('Proponer mejoras en procesos, organización del trabajo, comunicación operativa y coordinación entre áreas. ', False),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('Asesorar en el diseño de medidas relacionadas con jornadas, rotación de turnos, pausas, descansos y cobertura de personal. ', False),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('Apoyar en la definición de indicadores operativos y de calidad vinculados con las medidas de intervención. ', False),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('Evaluar la viabilidad técnica de las recomendaciones antes de su implementación. ', False),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('12.3. Responsable interno del centro de trabajo', True),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('[Nombre del responsable interno]', True),
            ('\n', False),
            ('[Puesto]', True),
            ('\n', False),
            ('[Área]', True),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('Será responsable de:', False),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('Diseñar y coordinar internamente la ejecución del Programa de intervención. ', False),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('Gestionar los recursos humanos, materiales y administrativos necesarios. ', False),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('Convocar a las áreas responsables. ', False),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('Vigilar el cumplimiento de los plazos establecidos. ', False),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('Integrar y conservar las evidencias de implementación. ', False),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('Informar a la dirección sobre los avances, dificultades y resultados. ', False),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('Coordinar la comunicación de las acciones a los trabajadores. ', False),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('Canalizar y atender a los casos individuales identificados en ATS, Violencia laboral y alto y muy alto. ', False),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
            ('Dar seguimiento a los mecanismos de queja, atención y canalización.', False),
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
        ],
    },
    {
        'style': 'Normal',
        'align': None,
        'segs': [
        ],
    },
]

# ---------------------------------------------------------------------------
# Constantes con datos dinámicos por planta (placeholders .format()).
# ---------------------------------------------------------------------------

# §5 Justificación de la muestra — primer párrafo con "Ecuación 1" en negrita.
JUSTIFICACION_P1_SEGS = [
    ('De acuerdo con lo establecido en la NOM-035-STPS-2018, para centros de '
     'trabajo con más de 50 trabajadores la evaluación debe aplicarse a una '
     'muestra representativa del total de la plantilla. El tamaño mínimo de '
     'muestra se calculó mediante la ', False),
    ('Ecuación 1', True),
    (' de la norma, utilizando un nivel de confianza del 95% (Z = 1.96), '
     'probabilidad de ocurrencia p = q = 0.5 y margen de error del 5%, '
     'garantizando así la validez estadística de los resultados.', False),
]

# §9.2 / §9.3 — introducción de los rangos oficiales (cursiva).
INTRO_RANGOS_CATEGORIA = ('Rangos oficiales de calificación por categoría — '
                          'Guía de Referencia III.')
INTRO_RANGOS_DOMINIO = ('Rangos oficiales de calificación por dominio — '
                        'Guía de Referencia III.')

# §9.2 / §9.3 — nota de denominador SIN la frase final "No existe un nivel
# global oficial del centro derivado del promedio." (retirada por dirección).
# La de categorías conserva un espacio final; la de dominios no.
NOTA_NIVELES = ('Los niveles se clasifican por cuestionario individual con los '
                'puntos de corte oficiales (Tabla 6, Guía de Referencia III). '
                '"Medio o superior" es la referencia para el Programa de '
                'intervención (Tabla 7); "Alto o Muy alto" indica prioridad '
                'elevada.')

# §10 Conclusiones — dos párrafos de introducción (estilos del documento
# aprobado) y párrafos de 10.1 con cifras en negrita.
CONCLUSIONES_INTRO_1 = ('Con base en los resultados obtenidos mediante la '
                        'aplicación de la Guía de Referencia III de la '
                        'NOM-035-STPS-2018, correspondiente a {n} trabajadores '
                        'evaluados, se presentan las siguientes conclusiones.')
CONCLUSIONES_INTRO_2 = ('De conformidad con el apartado III.4 de la Guía de '
                        'Referencia III, el nivel de riesgo se determina a '
                        'partir de la calificación de cada cuestionario '
                        'individual. Las acciones para el control de los '
                        'factores de riesgo psicosocial se establecen con base '
                        'en los criterios de la Tabla 7, la cual contempla la '
                        'implementación o fortalecimiento de un Programa de '
                        'intervención para los niveles Medio, Alto y Muy alto.')

CONCLUSION_10_1_P1 = [
    ('De los ', False),
    ('{n} trabajadores evaluados', True),
    (', ', False),
    ('{acc} personas ({pct_acc} %)', True),
    (' obtuvieron una calificación final individual en los niveles Medio, '
     'Alto o Muy alto. En consecuencia, los resultados muestran la necesidad '
     'de establecer o fortalecer acciones para el control de los factores de '
     'riesgo psicosocial mediante un Programa de intervención, conforme a los '
     'criterios de la Tabla 7 de la Guía de Referencia III.', False),
]
CONCLUSION_10_1_P2 = [
    ('Dentro de este grupo, ', False),
    ('{alto} trabajadores ({pct_alto} %)', True),
    (' se ubicaron en los niveles Alto o Muy alto, por lo que requieren una '
     'atención prioritaria mediante el análisis de las categorías y dominios '
     'correspondientes, a fin de determinar las acciones de intervención más '
     'adecuadas.', False),
]
CONCLUSION_10_1_P3 = [
    ('El nivel individual con mayor frecuencia fue ', False),
    ('{nivel}', True),
    (', con ', False),
    ('{moda} trabajadores ({pct_moda} %)', True),
    ('. Este resultado corresponde a la moda de la distribución de los '
     'cuestionarios individuales y se presenta únicamente como un indicador '
     'descriptivo; no constituye una calificación oficial global del centro '
     'de trabajo.', False),
]

CONCLUSION_10_2_INTRO = ('A continuación, se presentan las cinco categorías '
                         'evaluadas, ordenadas de mayor a menor porcentaje de '
                         'población en niveles Alto y Muy alto (indicador '
                         'interno de priorización).')

SINTESIS_SEGS = [
    ('En síntesis, el {pct_acc}% de los trabajadores evaluados obtuvo una '
     'calificación final en niveles Medio, Alto o Muy alto, por lo que se '
     'requiere la adopción de acciones mediante un Programa de intervención, '
     'conforme a la Tabla 7 del apartado III.4 de la Guía III. ', False),
    ('La categoría que concentra el mayor porcentaje de trabajadores en '
     'niveles Alto y Muy alto es "{cat}", y el dominio con mayor prioridad de '
     'atención es "{dom}".', True),
    (' Se recomienda implementar las acciones descritas en la sección 11 de '
     'este informe, priorizando las áreas identificadas.', False),
]

# Guía I (Anexo A.T.2) — restauración de acentos/¿ de los catálogos de BD
# (la BD guarda los reactivos sin acentos; el informe los presenta con la
# ortografía oficial de la NOM).
ATS_ACENTOS = {
    'Accidente que tenga como consecuencia la muerte, la perdida de un miembro o una lesion grave.':
        'Accidente que tenga como consecuencia la muerte, la pérdida de un miembro o una lesión grave.',
    'Ha tenido recuerdos recurrentes sobre el acontecimiento que le provocan malestares?':
        '¿Ha tenido recuerdos recurrentes sobre el acontecimiento que le provocan malestares?',
    'Ha tenido suenos de caracter recurrente sobre el acontecimiento, que le producen malestar?':
        '¿Ha tenido sueños de carácter recurrente sobre el acontecimiento, que le producen malestar?',
    'Se ha esforzado por evitar todo tipo de sentimientos, conversaciones o situaciones que le puedan recordar el acontecimiento?':
        '¿Se ha esforzado por evitar todo tipo de sentimientos, conversaciones o situaciones que le puedan recordar el acontecimiento?',
    'Se ha esforzado por evitar todo tipo de actividades, lugares o personas que motivan recuerdos del acontecimiento?':
        '¿Se ha esforzado por evitar todo tipo de actividades, lugares o personas que motivan recuerdos del acontecimiento?',
    'Ha tenido dificultad para recordar alguna parte importante del evento?':
        '¿Ha tenido dificultad para recordar alguna parte importante del evento?',
    'Ha disminuido su interes en sus actividades cotidianas?':
        '¿Ha disminuido su interés en sus actividades cotidianas?',
    'Se ha sentido usted alejado o distante de los demas?':
        '¿Se ha sentido usted alejado o distante de los demás?',
    'Ha notado que tiene dificultad para expresar sus sentimientos?':
        '¿Ha notado que tiene dificultad para expresar sus sentimientos?',
    'Ha tenido la impresion de que su vida se va a acortar, que va a morir antes que otras personas o que tiene un futuro limitado?':
        '¿Ha tenido la impresión de que su vida se va a acortar, que va a morir antes que otras personas o que tiene un futuro limitado?',
    'Ha tenido usted dificultades para dormir?':
        '¿Ha tenido usted dificultades para dormir?',
    'Ha estado particularmente irritable o le han dado arranques de coraje?':
        '¿Ha estado particularmente irritable o le han dado arranques de coraje?',
    'Ha tenido dificultad para concentrarse?':
        '¿Ha tenido dificultad para concentrarse?',
    'Ha estado nervioso o constantemente en alerta?':
        '¿Ha estado nervioso o constantemente en alerta?',
    'Se ha sobresaltado facilmente por cualquier cosa?':
        '¿Se ha sobresaltado fácilmente por cualquier cosa?',
}
