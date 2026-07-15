# Auditoría metodológica NOM-035-STPS-2018

**Fecha:** 2026-07-14
**Fuente normativa:** NOM-035-STPS-2018 (DOF 23-oct-2018), texto oficial
<https://asinom.stps.gob.mx/upload/nom/48.pdf> — verificado directamente contra el PDF
(Guía de Referencia I, II, III y V; Tablas 5, 6 y 7; Ecuación 1; numerales 5, 7 y 8).
**Alcance:** `backend/m06_results/`, `backend/documents/`, `backend/m00_onboarding/`,
`backend/m05_questionnaires/`, `generar_informe.py`, frontend (gráficas de resultados).

Convención de prioridad: **Crítica** (altera resultados normativos o expone datos),
**Alta** (riesgo metodológico serio o de interpretación), **Media** (calidad/trazabilidad),
**Baja** (estilo/documentación).

---

## 0. Verificación de constantes normativas contra el texto oficial

Antes de los hallazgos, se contrastaron las constantes del motor
(`backend/m06_results/scoring.py`) contra el PDF oficial:

| Elemento | Resultado de la verificación |
|---|---|
| Tabla 5 — ítems con calificación invertida (Siempre=0): 1, 4, 23–28, 30–53, 55, 56, 57 | ✅ `_GUIA_III_INVERSOS` coincide exactamente (el ítem 29 y el 54 son directos, como en la NOM). |
| Cortes Cfinal: <50, <75, <99, <140, ≥140 | ✅ `_CORTES_FINAL` coincide. |
| Cortes de las 5 categorías | ✅ `_CORTES_CATEGORIA` coincide con GR.III III.3.c.2. |
| Cortes de los 10 dominios | ✅ `_CORTES_DOMINIO` coincide con GR.III III.3.c.3 (incluye Jornada 1/2/4/6 y Violencia 7/10/13/16). |
| Integración de ítems por dominio (Tabla 6) | ✅ El mapeo posicional bloque→ítem (offsets `_GUIA_III_ITEM_OFFSET`) y las divisiones D5/D8/D11 reproducen la Tabla 6. |
| Criterio Guía I (GR.I incisos a y b) | ✅ Sección I ≥1 "Sí" **y** (II ≥1 **o** III ≥3 **o** IV ≥2), umbrales independientes por sección. |
| Ecuación 1 | ✅ `n = 0.9604·N / (0.0025·(N−1) + 0.9604)`, redondeo hacia arriba. |
| Tabla 6 — 25 dimensiones | ⚠️ **No estaban implementadas.** La asignación oficial verificada (que difiere de versiones citadas informalmente) es: Condiciones peligrosas e inseguras = 1, 3; Condiciones deficientes e insalubres = 2, 4; Trabajos peligrosos = 5; **Inestabilidad laboral = 53, 54; Limitado sentido de pertenencia = 55, 56**; etc. Ver `_DIMENSIONES` en `scoring.py`. |
| Tabla 7 — criterios para la toma de acciones | ⚠️ Los textos usados en el informe (`ACCIONES_CUADRO2`) **no** eran los oficiales: añadían obligaciones (exámenes médicos en nivel Medio, seguimiento mensual, canalización urgente) que la Tabla 7 no contiene en esos términos. |

Nota interpretativa documentada: la notación del DOF ("50<Cfinal<75") es inclusiva en el
límite inferior (50 ≤ Cfinal < 75); es la lectura estándar y la única que produce rangos
exhaustivos y mutuamente excluyentes. No se modificó ningún punto de corte oficial.

---

## 1. Hallazgos

### H-01 · Respuestas faltantes convertidas en cero — **Crítica**
- **Archivo/función:** `backend/m06_results/scoring.py::_valor_item_guia_iii` (`if not respuesta or respuesta.valor is None: return 0`).
- **Riesgo metodológico:** Un cuestionario incompleto se calificaba como si el trabajador hubiera respondido la opción de menor riesgo (o de mayor riesgo en ítems invertidos, donde 0 crudo se convertía en 4). Subestima o sobreestima Cfinal de forma silenciosa.
- **Consecuencia:** Clasificaciones individuales inválidas; trabajadores en riesgo pueden quedar en "nulo" y viceversa; el agregado organizacional hereda el sesgo.
- **Corrección:** Motor v2: validación estructurada previa (`validar_guia_iii`); un ítem obligatorio faltante invalida el cálculo (estatus `requiere_revision`), nunca se imputa 0 ni promedio.
- **Estado:** ✅ Corregido (motor v2 + persistencia de estatus de validación).

### H-02 · Sin validación de completitud, rango ni duplicados — **Crítica**
- **Archivo/función:** `scoring.py::calcular_resultado` y `m06_results/views.py::calcular` (calculaba cualquier aplicación con `estado='completado'` sin verificar contenido).
- **Riesgo:** Valores fuera de 0–4, preguntas sin responder o respuestas nulas entraban directo a la suma.
- **Corrección:** Resultado de validación estructurado (`es_valido`, `errores_criticos`, `advertencias`, `reactivos_faltantes`, `reactivos_fuera_de_rango`, `inconsistencias_filtros`, `version_motor`); las aplicaciones inválidas no generan clasificación y quedan reportadas.
- **Estado:** ✅ Corregido.

### H-03 · Filtros condicionados (ítems 65–68 y 69–72) mal manejados — **Crítica**
- **Archivo/función:** `scoring.py::_filtro_contestado_si` — un filtro **faltante** se trataba igual que "No" (bloque excluido en silencio); un filtro "No" con reactivos contestados se ignoraba.
- **Riesgo:** GR.III exige contestar el cuestionario completo; un filtro sin responder es un cuestionario incompleto, no un "No aplica".
- **Corrección:** Reglas explícitas: filtro "Sí" + condicionado faltante → incompleto; filtro "No" + condicionados vacíos → válido; filtro "No" + condicionados contestados → advertencia registrada (los condicionados no suman); filtro faltante → incompleto.
- **Estado:** ✅ Corregido (con pruebas de los cuatro escenarios).

### H-04 · Nivel de riesgo "global" del centro = clasificación del promedio — **Crítica**
- **Archivo/función:** `backend/documents/views.py::_build_context` (`nivel_global = _categoria_por_rangos(promedio_global, _CORTES_FINAL)`); replicado en `_riesgo_por_grupo` (sexo/edad/puesto/jornada), `areas_analisis` y documentado como correcto en `METODOLOGIA_CALCULOS.md` §5.
- **Riesgo:** Los puntos de corte de la Tabla 6 aplican a cuestionarios individuales. Clasificar el promedio comprime la distribución: un centro con 40 % de personas en "alto" puede promediar "bajo".
- **Consecuencia:** El informe podía declarar un nivel oficial del centro que la NOM no define y que oculta a la población en riesgo.
- **Corrección:** La conclusión principal se basa en la distribución de personas por nivel (nivel predominante = moda, % en medio+, % en alto+muy alto). El promedio se conserva solo como estadístico descriptivo con la nota obligatoria. Grupos (área/sexo/edad/puesto/jornada) reportan distribuciones, no niveles de promedio.
- **Estado:** ✅ Corregido en `documents/views.py` (contexto del informe) y documentación; el DOCX consume los nuevos campos.

### H-05 · Credenciales codificadas en el repositorio — **Crítica**
- **Archivo:** `generar_informe.py:30-31` (contraseña de PostgreSQL local en texto plano) y `credenciales_produccion.html` **versionado en git** (raíz del repo). También existen dumps de producción (`dump_produccion*.dump/json`) en la raíz.
- **Riesgo:** Exposición de credenciales y de datos personales de trabajadores ante cualquier persona con acceso al repositorio.
- **Corrección:** `generar_informe.py` ahora lee `NOM035_DB_*` de variables de entorno (sin valores por defecto para la contraseña). `credenciales_produccion.html` y `dump_produccion*` se agregaron a `.gitignore`; queda pendiente (decisión del usuario) retirarlos del índice (`git rm --cached`), purgar el historial y **rotar** las credenciales expuestas. Los valores encontrados no se reproducen en este informe.
- **Estado:** 🟡 Parcial — código corregido y `.gitignore` actualizado; rotación y purga de historial requieren acción del usuario.

### H-06 · Estratificación con `ceil` por estrato (la suma excede *n*) — **Crítica**
- **Archivo/función:** `backend/m00_onboarding/views.py::_estrato` (`ceil((N_e/N)·n)` por estrato) usado por `_con_muestra`.
- **Riesgo:** La suma de los estratos supera sistemáticamente el tamaño de muestra n (con 10 estratos puede sobrar hasta 9), y la proporción por sexo exigida por GR.III III.1 deja de ser exacta.
- **Corrección:** Método de restos mayores (`_estratos_restos_mayores`): parte entera de la cuota exacta + reparto de los lugares restantes por fracción mayor; la suma es exactamente n. `_estrato` se conserva como referencia de cuota mínima individual.
- **Estado:** ✅ Corregido (con pruebas de suma exacta).

### H-07 · Las 5 categorías oficiales no se calculaban en el motor ni se persistían — **Alta**
- **Archivo/función:** `scoring.py` definía `_CORTES_CATEGORIA` pero no lo usaba; la clasificación individual por categoría se recalculaba fuera del motor (`documents/views.py::_build_jerarquia_categorias/_build_anexos`), duplicando lógica.
- **Riesgo:** Dos rutas de cálculo para un resultado oficial; imposible auditar desde BD el nivel por categoría de cada trabajador.
- **Corrección:** El motor calcula y el sistema persiste las 5 categorías por aplicación (`ResultadoCategoria`); el informe consume lo persistido.
- **Estado:** ✅ Corregido.

### H-08 · Las 25 dimensiones oficiales no existían; los bloques D1–D14 se presentaban como "Dimensiones" — **Alta**
- **Archivo/función:** `documents/views.py::_build_psico_context` (sección 9.4 "Dimensiones" = bloques D1–D14) y `scoring.py::_CUTOFFS_PCT` (semáforo porcentual inventado por bloque, sin sustento normativo).
- **Riesgo:** El informe presentaba una unidad de análisis inexistente en la NOM con niveles pseudo-oficiales; las dimensiones reales de la Tabla 6 no se reportaban.
- **Corrección:** Se implementaron las 25 dimensiones oficiales (suma, máximo posible, % del máximo — **sin niveles**, con la nota "Indicador descriptivo. La NOM-035-STPS-2018 no establece puntos de corte por dimensión."), persistidas en `ResultadoDimension`. Los bloques D1–D14 se conservan etiquetados como "Bloques internos de captura (análisis complementario no normativo)".
- **Estado:** ✅ Corregido en motor/modelos/contexto; el DOCX muestra las dimensiones oficiales como descriptivas.

### H-09 · Sin umbral de confidencialidad para grupos pequeños — **Alta**
- **Archivo/función:** `documents/views.py` (áreas y grupos demográficos con n=1 visibles), `m06_results/views.py::dominios_agregados` (por área sin umbral).
- **Riesgo:** Filtros por área/sexo/edad con grupos pequeños permiten identificar resultados individuales (violación de confidencialidad, numeral 8.3).
- **Corrección:** Umbral configurable `UMBRAL_CONFIDENCIALIDAD` (por defecto n<5, ajustable vía settings/env `NOM035_UMBRAL_CONFIDENCIALIDAD`); los grupos por debajo se reportan como "Dato reservado por confidencialidad".
- **Estado:** ✅ Corregido en agregaciones de backend.

### H-10 · Textos de acciones (Tabla 7) no oficiales — **Alta**
- **Archivo/función:** `documents/views.py::ACCIONES_CUADRO2` (llamado además "Cuadro 2", nombre que no existe en la NOM).
- **Riesgo:** Presentaba como obligación normativa acciones que la Tabla 7 no establece en esos términos (p. ej. exámenes médicos en nivel Medio sin la condición de signos/síntomas del numeral 5.7; "canalización urgente").
- **Corrección:** Se sustituyeron por la transcripción fiel de la Tabla 7 (verificada contra el PDF) bajo el nombre `ACCIONES_TABLA7`, separando en el informe las "Acciones previstas por la NOM" de las "Recomendaciones técnicas complementarias".
- **Estado:** ✅ Corregido.

### H-11 · Guía I sin validación ni persistencia de criterios por sección — **Alta**
- **Archivo/función:** `scoring.py::_calcular_guia_i` — un "Sí" faltante contaba como "No"; no se persistían los conteos por sección ni qué criterio (II/III/IV) se cumplió.
- **Riesgo:** Falsos negativos silenciosos en un instrumento cuyo fin es canalizar a valoración clínica; imposible auditar el motivo de la canalización.
- **Corrección:** Validación (Sección I completa obligatoria; si hay algún "Sí" en Sección I, las secciones II–IV son obligatorias; si toda la Sección I es "No", II–IV pueden omitirse conforme a GR.I inciso a). El resultado incluye `seccion_i..iv`, `cumple_criterio_ii/iii/iv` y `estatus_validacion`, persistidos en `ResultadoAplicacion.detalle`.
- **Estado:** ✅ Corregido.

### H-12 · Lógica normativa duplicada fuera del motor — **Alta**
- **Archivos:** `generar_informe.py:502-618` (copia completa de cortes e inversión + conexión directa a BD), `m05_questionnaires/models.py::RespuestaPregunta.valor_ponderado` (usa `Pregunta.inversa`, campo documentado como no confiable), `documents/views.py` (reclasificación propia), semáforo `_CUTOFFS_PCT`.
- **Riesgo:** Constantes contradictorias y resultados divergentes entre informe local y producción.
- **Corrección:** `scoring.py` queda como única fuente (expone API pública `CORTES_FINAL`, `CORTES_CATEGORIA`, `CORTES_DOMINIO`, `clasificar`); `valor_ponderado` se marcó como obsoleto (no usar para Guía III); `generar_informe.py` se marcó como script histórico congelado (encabezado de advertencia) — los informes de producción salen del backend.
- **Estado:** 🟡 Parcial — backend unificado; `generar_informe.py` se conserva como histórico documentado (no se reescribió).

### H-13 · Sin trazabilidad: versión de motor, hash, fechas, unicidad — **Media**
- **Archivo/función:** `m06_results/models.py` (solo puntaje/categoría/fecha auto_now).
- **Corrección:** `ResultadoAplicacion` ahora registra `version_motor`, `hash_respuestas` (SHA-256 de las respuestas ordenadas), `estatus_validacion`, `detalle` (JSON con validación completa y resultados estructurados), `fecha_calculo`. Recalcular es idempotente (mismo hash → mismos resultados) y transaccional. La unicidad por aplicación ya existía (`OneToOneField`).
- **Estado:** ✅ Corregido (migración `0004`, sin borrar datos históricos).

### H-14 · Descripciones de guías incorrectas — **Media**
- **Archivo/función:** `documents/views.py::GUIA_DESC` (`'I': 'hasta 15 trabajadores'`, `'III': '16 a 50'`, `'V': 'más de 50'`).
- **Riesgo:** Confunde la Guía I (ATS, aplica a todos los centros) con los umbrales de los numerales 7.1/7.2 (Guía II: centros de 16 a 50; Guía III: más de 50). La Guía V son datos del trabajador, no un cuestionario de riesgo.
- **Corrección:** Textos corregidos conforme a los numerales 7.1–7.4 y a las propias guías.
- **Estado:** ✅ Corregido.

### H-15 · Informe demográfico sin denominadores válidos ni control de faltantes — **Media**
- **Archivo/función:** `documents/views.py::_build_muestra` y `_distribucion_simple` (mezcla "Sin dato" con las categorías, sin N válido/faltante; universo = trabajadores con cualquier aplicación del ciclo, no la población analítica de Guía III).
- **Corrección:** `_distribucion_simple` separa `n_valido`/`n_faltante` y calcula porcentajes sobre el N válido; el universo demográfico se alinea con los trabajadores con Guía III válida (declarado en el informe).
- **Estado:** 🟡 Parcial — denominadores corregidos; normalización de antigüedad a meses con reglas documentadas queda pendiente (los campos actuales están en años).

### H-16 · Gráficas con problemas metodológicos/visuales — **Media**
- **Archivos:** `generar_informe.py::_ats_chart` (`bar3d`, gráfica 3D prohibida por buenas prácticas), `documents/views.py::_build_graficas_informe` (pastel para la distribución de 5 niveles), gráficas sin N/nota metodológica sistemática.
- **Corrección:** En el flujo de producción, la distribución de niveles usa barra apilada 100 % y las gráficas llevan N y nota; el 3D solo existe en el script histórico congelado.
- **Estado:** 🟡 Parcial — datos y notas corregidos en el contexto; el rediseño visual completo (paleta accesible con icono/patrón, Likert divergente de violencia, mapa de calor con umbral) queda en pendientes.

### H-17 · Datos de empresa codificados de forma fija — **Media**
- **Archivo:** `documents/contenido_normativo.py::RAZON_SOCIAL / ACTIVIDAD_PRINCIPAL` usados para *todos* los tenants (`documents/views.py::datos_centro_trabajo`).
- **Riesgo:** Un informe de otro cliente saldría con la razón social de este cliente.
- **Corrección:** Se usa `tenant.razon_social` (con fallback al valor configurado solo si el tenant no lo define) — los datos fijos dejan de estar en la ruta multi-tenant.
- **Estado:** ✅ Corregido en el contexto del informe (con fallback conservador para no romper informes del cliente actual).

### H-18 · Anexo con resultados individuales dentro del informe general — **Alta**
- **Archivo/función:** `documents/views.py::_build_anexos` — el informe general incluye tablas 13.x con folio (número de empleado), calificación final, nivel y estatus ATS de **cada** trabajador, y `_build_context` lista trabajadores por nombre cuando `anonimo=False`.
- **Riesgo:** El número de empleado es un identificador directo; los resultados individuales y la canalización clínica deben vivir en un anexo confidencial separado del informe general (numeral 8.3 y principio de confidencialidad de GR.V).
- **Corrección:** El contexto marca estas secciones como `anexo_confidencial` y el generador puede excluirlas (`incluir_anexo_confidencial=False` por defecto en el informe general).
- **Estado:** 🟡 Parcial — separación lógica implementada en el contexto; falta el endpoint dedicado de anexo confidencial con registro de accesos.

### H-20 · Dashboard (frontend) clasificaba un promedio ponderado y usaba claves de dominio equivocadas — **Alta**
- **Archivo/función:** `frontend/src/components/resultados/useDashboardData.js` — el gauge "riesgo global" convertía la distribución en un promedio ponderado (0-4) y lo reclasificaba con cortes inventados (`scoreToCategoria`); el radar de 5 categorías agrupaba con claves de los *bloques de captura* (D1-D14) los datos del endpoint `dominios-agregados`, que entrega los *dominios oficiales* (D1-D10); el panel de violencia leía `D12` (inexistente en datos oficiales — la Violencia oficial es `D8`), por lo que podía mostrar 0 %.
- **Riesgo:** El tablero mostraba un "nivel global" no normativo y un radar/panel de violencia con integraciones incorrectas.
- **Corrección:** El gauge muestra el nivel predominante (moda de niveles individuales); el radar usa la correspondencia oficial categoría→dominios (D1 / D2-D3 / D4-D5 / D6-D8 / D9-D10) con el peor nivel modal como indicador visual; violencia lee el dominio oficial D8.
- **Estado:** ✅ Corregido (build de frontend verificado).

### H-19 · Cuestionarios "en progreso" y duplicados no auditados — **Baja**
- `unique_together ('aplicacion','pregunta')` y `('ciclo','cuestionario','trabajador')` ya previenen duplicados en BD. El flujo de muestra (población → seleccionados → iniciadas → completadas → excluidas → válidas → analizadas) se agregó al contexto del informe.
- **Estado:** ✅ Cubierto por restricciones existentes + tabla de flujo nueva.

---

## 2. Resumen de prioridades

| Prioridad | Hallazgos | Estado |
|---|---|---|
| Crítica | H-01, H-02, H-03, H-04, H-05, H-06 | 5 corregidos, H-05 parcial (requiere rotación de credenciales por el usuario) |
| Alta | H-07, H-08, H-09, H-10, H-11, H-12, H-18, H-20 | 6 corregidos, 2 parciales |
| Media | H-13, H-14, H-15, H-16, H-17 | 3 corregidos, 2 parciales |
| Baja | H-19 | Cubierto |

## 3. Limitaciones y pendientes (decisión/es del usuario)

1. **Rotar credenciales** expuestas en `credenciales_produccion.html` y purgar el historial de git (`git filter-repo`). Los archivos ya están en `.gitignore`; falta `git rm --cached` y commit (acción destructiva sobre el índice: se dejó al usuario).
2. Retirar de la raíz los dumps de producción (`dump_produccion*.dump/.json`) que contienen datos personales.
3. Endpoint de **anexo confidencial** separado (folio→trabajador→criterio→canalización→seguimiento) con bitácora de accesos.
4. Rediseño visual completo de gráficas (paleta accesible con etiqueta+icono, Likert divergente para violencia 57–64 distinguiendo el ítem protector 57, mapa de calor dominio×área con umbral de confidencialidad, panel ejecutivo).
5. Normalización de antigüedad/experiencia a meses con marcado de valores ambiguos.
6. Exportación XLSX de 14 hojas y JSON auditable por endpoint (el XLSX actual exporta respuestas crudas y el DOCX; faltan hojas de metodología/calidad/intervención).
7. Snapshot inmutable de informes emitidos (el hash + versión de motor ya permiten reproducir; falta congelar el JSON del contexto por informe aprobado).
8. Selección aleatoria reproducible con semilla registrada cuando el sistema haga la selección de la muestra (hoy la selección es manual/externa).
9. `generar_informe.py` (script histórico) conserva su propia copia de constantes: está congelado y marcado como no-fuente-de-verdad; si se vuelve a usar, debe portarse a consumir `m06_results.scoring`.

## 4. Decisiones metodológicas documentadas

1. Límite inferior inclusivo en todos los cortes (lectura estándar del DOF).
2. Un cuestionario Guía III es **válido** solo si: los 64 ítems incondicionales están respondidos en rango 0–4, ambos filtros están respondidos, y los bloques condicionados aplicables están completos. Cualquier otra cosa → `requiere_revision` (no se clasifica).
3. Filtro "No" con reactivos condicionados contestados: advertencia (no invalida); los reactivos condicionados **no** se suman, porque el trabajador declaró que no aplican.
4. El "nivel del centro de trabajo" se comunica como *nivel predominante* (moda de niveles individuales) + distribución completa; nunca como clasificación del promedio.
5. Umbral de confidencialidad por defecto: n < 5 (configurable a n < 10 vía `NOM035_UMBRAL_CONFIDENCIALIDAD`).
6. Índice de priorización complementario: orden por (% alto+muy alto, % medio+, mediana, N expuestos) — documentado y etiquetado como no normativo.
7. Escala en BD confirmada: `RespuestaPregunta.VALOR_CHOICES` almacena Nunca=0 … Siempre=4; la inversión oficial se aplica como `4 − valor` a los ítems de la Tabla 5 por número de ítem (el campo `Pregunta.inversa` NO se usa para Guía III).
