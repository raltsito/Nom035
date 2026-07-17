"""Estructura canónica del Informe Diagnóstico NOM-035 (formato aprobado).

Secuencia exacta de encabezados (texto y nivel Word) del documento maestro
de Zapotitlán (PLANTA Zapot-2.pdf). Notas deliberadas:

- NO existe `9.4`: las dimensiones viven en el Anexo técnico como `A.T.3`.
  No debe "corregirse" esa numeración sin decisión de dirección.
- `A.T.3` va sin punto después del 3, tal cual el maestro.
- El anexo confidencial (sección 13) NO forma parte de la estructura
  canónica: solo se añade bajo demanda (?anexo_confidencial=1).
"""

# (texto, nivel de encabezado Word)
ESTRUCTURA_CANONICA = [
    ('1. Índice', 1),
    ('Panel ejecutivo', 1),
    ('2. Datos del centro de trabajo', 1),
    ('2.1. Centro de trabajo', 3),
    ('2.2. Domicilio', 3),
    ('2.3. Actividad principal', 3),
    ('3. Objetivo', 1),
    ('3.1. Objetivo general', 3),
    ('3.2. Objetivos específicos', 3),
    ('4. Definiciones', 1),
    ('5. Justificación de la muestra', 1),
    ('6. Metodología', 1),
    ('6.1. Objetivo de la evaluación', 3),
    ('6.2. Instrumentos utilizados', 3),
    ('6.3. Procedimiento de aplicación', 3),
    ('6.4. Procesamiento a digital', 3),
    ('6.5. Evaluación y análisis de resultados', 3),
    ('Tasa de respuesta por instrumento', 3),
    ('7. Informe demográfico', 1),
    ('7.1. Informe de datos generales', 3),
    ('7.1.1. Informe de datos laborales', 3),
    ('8. Informe de acontecimientos traumáticos severos (ATS)', 1),
    ('9. Informe diagnóstico sobre los factores de riesgo psicosocial y del entorno organizacional', 1),
    ('9.1. Calificación final', 3),
    ('9.2. Calificaciones por categoría', 3),
    ('9.3. Calificaciones por dominio', 3),
    ('9.5. Áreas prioritarias', 3),
    ('9.6. Violencia laboral (resumen)', 3),
    ('10. Conclusiones', 1),
    ('10.1. Calificación final', 3),
    ('10.2. Análisis por categoría', 3),
    ('10.3. Análisis por dominio', 3),
    ('11. Recomendaciones', 1),
    ('11.1. Recomendaciones generales', 3),
    ('11.2. Recomendaciones específicas', 3),
    ('Matriz de intervención', 3),
    ('12. Datos del responsable de la evaluación', 1),
    ('Anexo técnico', 1),
    ('A.T.1. Bloques internos de captura (análisis complementario no normativo)', 3),
    ('A.T.2. Guía I — desglose por reactivo', 3),
    ('A.T.3 Dimensiones (indicador descriptivo)', 3),
]

TEXTOS_CANONICOS = [t for t, _ in ESTRUCTURA_CANONICA]
