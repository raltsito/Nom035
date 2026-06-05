# Plan de Resultados NOM-035-STPS-2018

> Objetivo: que la pestaña de Resultados calcule, muestre y exporte exactamente lo que
> la norma exige — sin datos inventados, con los umbrales oficiales, separando
> correctamente Guía I (ATS) y Guía III (factores psicosociales) —
> y que las visualizaciones sean impactantes, animadas y modernas.

---

## Diagnóstico del estado actual

### Problemas críticos encontrados

| # | Área | Problema |
|---|------|----------|
| 1 | `scoring.py` | `GUIA_III_DOMINIOS` cubre D1–D10, pero el cuestionario tiene **14 dominios**. D11–D14 no se califican. |
| 2 | `scoring.py` | Rangos de puntaje por dominio no coinciden con el número real de preguntas (D2: 3 ítems máx 12 pts, pero el rango llega a 37). |
| 3 | `scoring.py` | Guía I: umbral incorrecto. La norma exige ≥ 1 acontecimiento D1 **Y** ≥ 2 síntomas en D2+D3+D4. |
| 4 | `useDashboardData.js` | `HIST_FACTOR` — coeficientes ficticios para simular ciclo anterior. **Dato fabricado.** |
| 5 | `useDashboardData.js` | `atsTypes` — tipología con porcentajes fijos inventados. **Dato fabricado.** |
| 6 | `useDashboardData.js` | Radar usa D1–D5 como macro-dimensiones — mapping incorrecto. |
| 7 | `useDashboardData.js` | Donut de violencia usa D4+D5 en vez del dominio D12 real. |
| 8 | `useDashboardData.js` | Hace N requests individuales por trabajador al cargar (1 request por cada resultado). |
| 9 | `views.py` | `resumen` no devuelve trabajadores Guía I que requieren atención clínica. |
| 10 | `views.py` | No existe endpoint para puntajes agregados por dominio. |
| 11 | Bento Grid | `LineHistorica`, `BarTipologiaATS` y `PieATS` muestran datos fabricados. |
| 12 | Bento Grid | `DonutCumplimiento` — donut para dos números, desperdicio de espacio. |
| 13 | Bento Grid | `DonutViolencia` — redundante con `BarDominios`. |
| 14 | Bento Grid | `StackedBarPoblacion` mezcla Guía I y III que no son comparables. |
| 15 | Bento Grid | No existe heatmap dominios × áreas (la visualización más accionable de la norma). |
| 16 | Todas las gráficas | Diseño plano, sin animaciones, sin impacto visual. |

---

## Estructura NOM-035 de referencia

### Guía I — Identificación de ATS
- **D1:** 6 preguntas de acontecimiento traumático (sí/no).
- **D2–D4:** síntomas post-traumáticos (condicionales a D1).
- **Resultado:** Requiere evaluación clínica si ≥ 1 positivo en D1 **Y** ≥ 2 positivos en D2+D3+D4.
- No hay nivel numérico — resultado binario: "Requiere atención" / "Sin indicadores".

### Guía III — Factores de riesgo psicosocial (72 reactivos, 14 dominios)

| Puntuación global | Nivel de riesgo |
|---|---|
| < 20 | Nulo o despreciable |
| 20 – 44 | Bajo |
| 45 – 79 | Medio |
| 80 – 140 | Alto |
| > 140 | Muy alto |

D13 (Atención a clientes) y D14 (Actitudes de supervisados) son opcionales —
se suman solo si el trabajador respondió "Sí" a la pregunta filtro.

### Rangos oficiales por dominio — Guía III

| Dom. | Nombre | Ítems | Máx | Nulo | Bajo | Medio | Alto | Muy alto |
|---|---|---|---|---|---|---|---|---|
| D1 | Condiciones en el ambiente | P1–P5 | 20 | 0–2 | 3–5 | 6–11 | 12–16 | ≥17 |
| D2 | Ritmo de trabajo | P6–P8 | 12 | 0 | 1–2 | 3–5 | 6–8 | ≥9 |
| D3 | Esfuerzo mental | P9–P12 | 16 | 0–3 | 4–6 | 7–9 | 10–12 | ≥13 |
| D4 | Actividades y responsabilidades | P13–P16 | 16 | 0–1 | 2–3 | 4–7 | 8–12 | ≥13 |
| D5 | Jornada de trabajo | P17–P22 | 24 | 0–2 | 3–6 | 7–11 | 12–19 | ≥20 |
| D6 | Decisiones en el trabajo | P23–P28 inv. | 24 | 0–3 | 4–8 | 9–13 | 14–18 | ≥19 |
| D7 | Cambios en el trabajo | P29–P30 inv. | 8 | 0 | 1–2 | 3–4 | 5–6 | ≥7 |
| D8 | Capacitación | P31–P36 inv. | 24 | 0–3 | 4–8 | 9–13 | 14–17 | ≥18 |
| D9 | Liderazgo / Subordinación | P37–P41 inv. | 20 | 0–2 | 3–5 | 6–9 | 10–14 | ≥15 |
| D10 | Relaciones con compañeros | P42–P46 inv. | 20 | 0–2 | 3–5 | 6–9 | 10–14 | ≥15 |
| D11 | Rendimiento y reconocimiento | P47–P56 mix. | 40 | 0–5 | 6–12 | 13–20 | 21–30 | ≥31 |
| D12 | Violencia laboral | P57–P64 mix. | 32 | 0 | 1–3 | 4–6 | 7–12 | ≥13 |
| D13* | Atención a clientes | P65–P68 | 16 | 0 | 1–2 | 3–5 | 6–10 | ≥11 |
| D14* | Actitudes de supervisados | P69–P72 | 16 | 0 | 1–2 | 3–5 | 6–10 | ≥11 |

> *Solo aplican si respondieron "Sí" a la pregunta filtro correspondiente.

---

## Nuevo lineup de gráficas

### Gráficas que se eliminan

| Componente | Razón |
|---|---|
| `LineHistorica` | Datos completamente fabricados con `HIST_FACTOR` |
| `BarTipologiaATS` | Tipología inventada con porcentajes fijos |
| `PieATS` | Reemplazado por tabla real de Guía I |
| `DonutCumplimiento` | Donut para dos números — innecesariamente complejo |
| `DonutViolencia` | Redundante con `BarDominios` que ya cubre D12 |

### Gráficas que se corrigen

| Componente | Corrección |
|---|---|
| `RadarCategorias` | Mapeo correcto de 5 macro-dimensiones NOM-035 |
| `BarDominios` | Ampliar a 14 dominios, datos del nuevo endpoint |
| `StackedBarPoblacion` | Cambiar eje de "por guía" a "por perfil demográfico (Guía V)" |

### Gráficas que se mantienen

| Componente | Estado |
|---|---|
| `GaugeRiesgo` | ✅ Datos ya correctos |
| `BarDepartamentos` | ✅ Datos ya correctos |

### Gráficas nuevas

| Componente nuevo | Descripción |
|---|---|
| `HeatmapDominiosAreas` | Heatmap dominios (filas) × áreas (columnas), celda coloreada por nivel de riesgo. La visualización más accionable de la norma. |
| `TablaAtencionClinica` | Lista de trabajadores Guía I que requieren evaluación clínica, con tipo de acontecimiento y síntomas. |
| `CardTop3Dominios` | Tres tarjetas animadas mostrando los dominios con nivel de riesgo más alto — lectura inmediata para un directivo. |

### Bento Grid final

```
┌──────────────┐ ┌────────────────────────┐ ┌──────────────────────┐
│  GaugeRiesgo │ │  CardTop3Dominios       │ │  RadarCategorias     │
│  (animado)   │ │  (3 tarjetas animadas)  │ │  (5 macro-dims.)     │
└──────────────┘ └────────────────────────┘ └──────────────────────┘
┌─────────────────────────────────────────────────────────────────┐
│  BarDominios — 14 dominios horizontales con entrada animada     │
└─────────────────────────────────────────────────────────────────┘
┌────────────────────────────────┐ ┌──────────────────────────────┐
│  HeatmapDominiosAreas (NUEVO)  │ │  BarDepartamentos             │
│  dominios × áreas              │ │                               │
└────────────────────────────────┘ └──────────────────────────────┘
┌─────────────────────────────────────────────────────────────────┐
│  StackedBar por perfil demográfico (Guía V: puesto/jornada)     │
└─────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────┐
│  TablaAtencionClinica — Guía I (trabajadores con ATS)           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Sprints

---

### Sprint 1 — Motor de calificación correcto

**Objetivo:** `calcular_resultado()` produce puntajes y niveles de riesgo exactos
según la norma para todos los dominios.

#### Tareas

1. **Auditar rangos oficiales** contra el documento NOM-035 impreso.
2. **Reescribir `GUIA_III_DOMINIOS`** en `scoring.py`:
   - Agregar D11, D12, D13, D14.
   - Corregir D1–D10 para que coincidan con ítems reales.
3. **Corregir `GUIA_III_GLOBAL`**: < 20 / 20–44 / 45–79 / 80–140 / > 140.
4. **Corregir `_calcular_guia_i`**:
   - Umbral: D1 ≥ 1 positivo **Y** (D2+D3+D4) ≥ 2 positivos.
   - Retornar `requiere_atencion: bool`.
   - Categoría binaria: `'requiere_atencion'` / `'sin_indicadores'`.
5. **D13/D14 opcionales**: excluir del total si el trabajador no respondió el filtro.
6. **Tests unitarios**:
   - Guía III: puntaje conocido → nivel esperado.
   - Guía I: D1 positivo + ≥ 2 síntomas → `requiere_atencion=True`.
   - Guía I: D1 positivo + 1 síntoma → `requiere_atencion=False`.

#### Archivos
- `backend/m06_results/scoring.py`
- `backend/m06_results/models.py` (campo `requiere_atencion`)
- `backend/m06_results/migrations/`
- `backend/m06_results/tests.py`

---

### Sprint 2 — Endpoints backend completos

**Objetivo:** El frontend obtiene todos los datos que necesita sin fabricar nada.

#### Tareas

1. **Actualizar `calcular`** para persistir `requiere_atencion`.

2. **Extender `resumen`** (`GET /resultados/resumen/?ciclo_id=X`):
```json
{
  "total_resultados": 42,
  "total_completadas": 45,
  "total_aplicaciones": 50,
  "distribucion": { "nulo": 5, "bajo": 12, "medio": 15, "alto": 8, "muy_alto": 2 },
  "guia_i": {
    "total": 50, "completadas": 48,
    "requieren_atencion": 7, "sin_indicadores": 41
  },
  "guia_iii": {
    "total": 50, "completadas": 42,
    "distribucion": { "nulo": 5, "bajo": 12, "medio": 15, "alto": 8, "muy_alto": 2 }
  }
}
```

3. **Nuevo `dominios-agregados`** (`GET /resultados/dominios-agregados/?ciclo_id=X`):
```json
[
  {
    "dominio_clave": "D1",
    "dominio_nombre": "Condiciones en el ambiente",
    "puntaje_promedio": 8.3,
    "puntaje_max": 20,
    "pct_promedio": 41,
    "categoria_modal": "medio",
    "distribucion": { "nulo": 10, "bajo": 15, "medio": 12, "alto": 4, "muy_alto": 1 },
    "por_area": {
      "Producción": { "pct": 55, "categoria": "alto" },
      "Ventas": { "pct": 30, "categoria": "bajo" }
    }
  }
]
```
El campo `por_area` alimenta directamente el heatmap.

4. **Nuevo `atencion-clinica`** (`GET /resultados/atencion-clinica/?ciclo_id=X`):
   - Lista de trabajadores Guía I con `requiere_atencion=True`.
   - Incluye nombre, área, acontecimiento reportado (D1), síntomas positivos.

5. **Actualizar `ResultadoAplicacionSerializer`** para incluir `requiere_atencion`.

#### Archivos
- `backend/m06_results/views.py`
- `backend/m06_results/serializers.py`
- `backend/m06_results/models.py`
- `backend/m06_results/urls.py`
- `frontend/src/services/resultados.js`

---

### Sprint 3 — Refactorización de datos del dashboard

**Objetivo:** Eliminar todos los datos fabricados y conectar los endpoints reales.

#### Tareas

1. **Eliminar `HIST_FACTOR`** — quitar toda la lógica de datos históricos.
2. **Eliminar `atsTypes`** con porcentajes ficticios.
3. **Corregir `RADAR_DIMS`** con las 5 macro-dimensiones reales:
   - Dim 1: Condiciones del ambiente → D1
   - Dim 2: Factores propios de la actividad → D2 + D3 + D4
   - Dim 3: Organización del tiempo → D5
   - Dim 4: Liderazgo y relaciones → D9 + D10
   - Dim 5: Entorno organizacional → D6 + D7 + D8 + D11 + D12
4. **Eliminar los N requests individuales** por trabajador.
   - Reemplazar con `dominios-agregados` (1 solo request).
5. **Conectar `atencion-clinica`** para la nueva `TablaAtencionClinica`.
6. **Adaptar `StackedBarPoblacion`** para recibir datos demográficos de Guía V
   (agrupados por `tipo_puesto`: Operativo / Supervisor / Gerente / etc.).

#### Archivos
- `frontend/src/components/resultados/useDashboardData.js`
- `frontend/src/services/resultados.js`

---

### Sprint 4 — Rediseño visual: animaciones e impacto

**Objetivo:** Cada gráfica debe tener entrada animada, hover dinámico, paleta
coherente con la escala de riesgo NOM-035, y un diseño que impacte a primera vista.

#### Stack de animación recomendado

| Librería | Uso |
|---|---|
| **Framer Motion** | Entradas, transiciones de página, mount/unmount de componentes |
| **Recharts** custom shapes | Barras con gradiente, radiales personalizados |
| **CSS `@keyframes`** | Contadores animados, pulsos, glow en elementos críticos |
| **SVG nativo** | Gauge personalizado con arco animado, heatmap con interpolación de color |

#### Lineamientos de diseño global

- **Paleta de riesgo** coherente en todas las gráficas:
  - Nulo: `#10B981` (verde esmeralda)
  - Bajo: `#84CC16` (lima)
  - Medio: `#F59E0B` (ámbar)
  - Alto: `#EF4444` (rojo)
  - Muy alto: `#7C3AED` (violeta profundo)
- **Fondo de tarjetas**: glassmorphism sutil (`backdrop-filter: blur`, borde semitransparente).
- **Tipografía de números**: font-variant-numeric tabular, tamaño grande, peso bold.
- **Glow en elementos críticos**: los dominios con nivel "alto" o "muy_alto" tienen
  un glow sutil del color de riesgo.

#### Tareas por componente

**`GaugeRiesgo` — rediseño completo**
- SVG custom con arco degradado que va de verde a violeta.
- Aguja animada con `framer-motion` `useSpring` (rebote suave al llegar al valor).
- Número central con contador animado (0 → valor real).
- Anillo exterior con ticks para cada nivel de riesgo.

**`CardTop3Dominios` — nuevo componente**
- 3 tarjetas con glassmorphism.
- Entrada con `staggerChildren` (se revelan una tras otra con delay).
- Barra de puntaje que crece desde 0 al montar.
- Color de borde y glow según nivel del dominio.
- Número de dominio y nombre con truncado elegante.

**`RadarCategorias` — entrada y hover**
- `animationBegin={0}` + `animationDuration={1200}` de Recharts.
- Área con gradiente radial semitransparente.
- Tooltip custom con nombre completo de la macro-dimensión y puntaje %.
- Puntos en los vértices con hover que muestra detalle del dominio.

**`BarDominios` — 14 barras con entrada escalonada**
- Barras horizontales con gradiente de izquierda a derecha en el color del nivel.
- Entrada escalonada: cada barra crece con 40 ms de delay respecto a la anterior.
- Barras "alto" y "muy_alto" tienen un glow lateral pulsante.
- Etiqueta al final de cada barra con el nivel en texto.
- Al hacer hover: la barra se expande ligeramente y aparece tooltip con distribución
  (cuántos trabajadores en cada nivel para ese dominio).

**`HeatmapDominiosAreas` — nuevo componente SVG**
- Grid SVG puro: filas = 14 dominios, columnas = áreas de la empresa.
- Cada celda interpolada de verde a violeta según `pct_promedio`.
- Al hacer hover: la celda hace zoom sutil y aparece un tooltip flotante con
  `pct`, `categoria_modal` y N trabajadores.
- Celdas vacías (área sin trabajadores en ese dominio) muestran patrón diagonal sutil.
- Animación de entrada: las celdas aparecen en ola diagonal (top-left → bottom-right).

**`BarDepartamentos` — barras apiladas con animación**
- Cada segmento del stack entra con `animationBegin` escalonado por columna.
- Hover resalta solo el área hovered, desvanece el resto.
- Leyenda flotante que indica el total del área al hacer hover.

**`StackedBarPoblacion` — reenfocado a perfil**
- Misma mecánica visual que `BarDepartamentos`.
- Eje X: Operativo / Supervisor / Gerente / Técnico (desde Guía V).
- Tooltip con desglose de los 5 niveles de riesgo para ese perfil.

**`TablaAtencionClinica` — diseño de alerta**
- Fondo ligeramente tintado de rojo si hay casos, verde si no hay.
- Si hay casos: cada fila tiene un indicador pulsante (dot rojo animado).
- Si no hay casos: banner verde con checkmark animado (✓ que se dibuja con SVG stroke).
- Filas con hover que expande para ver los síntomas específicos.
- Contador animado en el encabezado: "X trabajadores requieren atención clínica".

#### Archivos
- `frontend/src/components/resultados/charts/GaugeRiesgo.jsx` (reescribir)
- `frontend/src/components/resultados/charts/BarDominios.jsx` (actualizar)
- `frontend/src/components/resultados/charts/RadarCategorias.jsx` (actualizar)
- `frontend/src/components/resultados/charts/BarDepartamentos.jsx` (actualizar)
- `frontend/src/components/resultados/charts/StackedBarPoblacion.jsx` (actualizar)
- `frontend/src/components/resultados/charts/HeatmapDominiosAreas.jsx` (nuevo)
- `frontend/src/components/resultados/charts/CardTop3Dominios.jsx` (nuevo)
- `frontend/src/components/resultados/charts/TablaAtencionClinica.jsx` (nuevo)
- `frontend/src/components/resultados/ResultadosDashboard.jsx` (reordenar Bento)
- `frontend/src/components/resultados/ResultadosDashboard.module.css`
- Eliminar: `LineHistorica.jsx`, `BarTipologiaATS.jsx`, `PieATS.jsx`,
  `DonutCumplimiento.jsx`, `DonutViolencia.jsx`

#### Dependencias a instalar
```bash
npm install framer-motion
```
> Recharts ya está instalado. D3 no es necesario — el heatmap se construye
> con SVG nativo y matemáticas simples de interpolación de color.

---

### Sprint 5 — Exportación e informe NOM-035

**Objetivo:** El PDF descargable contiene lo que la norma exige documentar.

#### Estructura del informe PDF

```
1. Portada: empresa, ciclo, fecha, firma responsable
2. Resumen ejecutivo: nivel de riesgo global, N trabajadores evaluados
3. Guía I — Trabajadores con ATS: tabla detallada con acontecimiento y síntomas
4. Guía III — Resultados individuales: puntaje y nivel global por trabajador
5. Guía III — Análisis por dominio: tabla de 14 dominios con nivel modal
6. Guía III — Análisis por área: distribución de niveles por departamento
7. Acciones requeridas según nivel de riesgo (Cuadro 2 de la norma)
8. Anexo: top 10 ítems con mayor puntaje promedio
```

#### Acciones requeridas por nivel (Cuadro 2 NOM-035)

| Nivel | Acción mínima |
|---|---|
| Nulo | Sin acción inmediata |
| Bajo | Acciones de mejora, revisar en siguiente ciclo |
| Medio | Plan de acción con plazos definidos |
| Alto | Acciones inmediatas, seguimiento mensual |
| Muy alto | Intervención urgente, evaluación clínica colectiva |

#### Tareas
1. Revisar el endpoint `GET /api/v1/documentos/informe-nom035/`.
2. Alimentarlo con datos de los endpoints del Sprint 2.
3. Agregar sección de Guía I.
4. Agregar tabla de 14 dominios.
5. Agregar tabla de acciones requeridas.

#### Archivos
- `backend/documents/` (vista del informe PDF)

---

## Orden de ejecución

```
Sprint 1 → Sprint 2 → Sprint 3 → Sprint 4 → Sprint 5
                                              ↑ puede
                                          paralelizarse
                                          con Sprint 4
```

Sprint 1 y 2 son bloqueantes (sin scoring correcto y endpoints completos,
el frontend no puede mostrar datos verdaderos).
Sprint 3 es bloqueante para Sprint 4.
Sprint 5 puede hacerse en paralelo con Sprint 4.

---

## Criterios de aceptación

### Sprint 1 ✓
- [x] `python manage.py test m06_results` pasa sin errores.
- [x] Trabajador con 0 síntomas no aparece como "requiere atención".
- [x] Recalcular un ciclo produce puntajes distintos a los actuales (evidencia de que los rangos cambiaron).

### Sprint 2 ✓
- [x] `GET /resultados/resumen/?ciclo_id=X` incluye `guia_i.requieren_atencion`.
- [x] `GET /resultados/dominios-agregados/?ciclo_id=X` devuelve 14 objetos con `por_area`.
- [x] `GET /resultados/atencion-clinica/?ciclo_id=X` devuelve lista correcta.
- [x] El total de requests HTTP al cargar el dashboard es ≤ 4.

### Sprint 3 ✓
- [x] `useDashboardData.js` no contiene `HIST_FACTOR` ni porcentajes ficticios.
- [x] Radar usa las 5 macro-dimensiones correctas de la norma.

### Sprint 4 ✓
- [x] El Gauge tiene aguja animada con rebote suave.
- [x] Las 14 barras de `BarDominios` entran escalonadas al montar el componente.
- [x] El heatmap muestra dominios × áreas con interpolación de color.
- [x] `TablaAtencionClinica` muestra banner verde si no hay casos.
- [x] `CardTop3Dominios` entra con `staggerChildren`.
- [x] No existen `LineHistorica.jsx`, `BarTipologiaATS.jsx`, `PieATS.jsx`,
      `DonutCumplimiento.jsx`, `DonutViolencia.jsx` en el proyecto.

### Sprint 5 ✓
- [x] El PDF incluye tabla de Guía I.
- [x] El PDF incluye resultados por los 14 dominios.
- [x] El PDF incluye las acciones requeridas según nivel de riesgo.

### Sprint 6 ✓
- [x] El reporte psicológico es descargable en PDF desde la plataforma.
- [x] Un psicólogo sin acceso al sistema puede leerlo y validarlo sin contexto adicional.
- [x] Cada hallazgo cita explícitamente el artículo o tabla de la NOM-035 que lo sustenta.
- [x] El reporte distingue claramente resultados de Guía I vs Guía III.
- [x] Las recomendaciones de intervención son concretas, no genéricas.

---

## Sprint 6 — Reporte psicológico para revisión de especialistas

**Objetivo:** Generar un documento en lenguaje clínico-organizacional que un psicólogo
pueda leer, validar y firmar sin necesidad de acceder al sistema.
No es el informe ejecutivo del Sprint 5 — es un documento técnico que expone
la metodología, los instrumentos, los hallazgos y las recomendaciones en los
términos que un especialista en salud mental laboral espera ver.

---

### Estructura del reporte psicológico

**1. Encabezado institucional**
- Nombre de la empresa, razón social, giro, N total de trabajadores.
- Ciclo evaluado, fechas de aplicación (inicio y cierre).
- Nombre del responsable de la evaluación (campo editable).
- Espacio para firma y cédula del psicólogo revisor.

**2. Marco normativo y metodológico**
- Fundamento legal: NOM-035-STPS-2018, Diario Oficial de la Federación,
  fecha de entrada en vigor.
- Instrumentos utilizados:
  - Guía de Referencia I: Identificación de Acontecimiento Traumático Severo (ATS).
  - Guía de Referencia III: Identificación y Análisis de Factores de Riesgo
    Psicosocial (72 reactivos, escala tipo Likert de frecuencia 0–4).
  - Guía de Referencia V: Datos del trabajador (variables sociodemográficas
    y laborales).
- Criterio de calificación de Guía I: se considera caso positivo cuando el
  trabajador reporta ≥ 1 acontecimiento traumático severo (Sección I) **y**
  ≥ 2 síntomas de las Secciones II, III y IV (recuerdos persistentes, evitación,
  afectación).
- Criterio de calificación de Guía III: puntaje por dominio y puntaje global
  comparado con los rangos normativos del Cuadro de puntajes oficial
  (5 niveles: Nulo / Bajo / Medio / Alto / Muy alto).

**3. Descripción de la muestra**
- Tabla sociodemográfica generada a partir de Guía V:
  - Distribución por sexo.
  - Distribución por grupo de edad.
  - Distribución por nivel de estudios.
  - Distribución por tipo de puesto (Operativo / Supervisor / Técnico / Gerente).
  - Distribución por tipo de jornada y rotación de turno.
  - Distribución por antigüedad en el puesto.
- Tasa de respuesta: N respondieron / N total (%) por guía.

**4. Resultados de Guía I — Acontecimiento Traumático Severo**
- Total de trabajadores que reportaron ≥ 1 acontecimiento (con %).
- Desglose de tipos de acontecimiento reportados (accidente, asalto, acto violento,
  secuestro, amenaza, otro) con frecuencia y porcentaje.
- Total de trabajadores que cumplen criterio de caso positivo (requieren
  evaluación clínica especializada), con % sobre la muestra.
- Tabla individual: nombre (o clave anónima si la empresa lo solicita), área,
  acontecimiento, síntomas positivos, recomendación.
- Nota clínica: los casos positivos no implican diagnóstico — se recomienda
  canalización a evaluación individual con psicólogo clínico o psiquiatra.

**5. Resultados de Guía III — Factores de Riesgo Psicosocial**

*5.1 Nivel de riesgo global de la organización*
- Puntaje promedio global y nivel de riesgo resultante.
- Distribución de trabajadores por nivel (tabla + %).
- Interpretación narrativa: qué significa ese nivel para la organización
  según la norma (texto estandarizado por nivel).

*5.2 Resultados por dominio*
- Tabla de 14 dominios con: puntaje promedio, nivel de riesgo, N trabajadores
  en cada nivel, dominio destacado como prioritario (si nivel ≥ Alto).
- Interpretación clínica breve por cada dominio en nivel Alto o Muy Alto:
  qué estresor psicosocial representa y qué consecuencias puede tener
  en salud mental si no se interviene.

*5.3 Análisis por variables sociodemográficas (Guía V)*
- Nivel de riesgo promedio por sexo, por grupo de edad, por tipo de puesto,
  por tipo de jornada.
- Identificar si algún grupo poblacional concentra niveles Alto o Muy Alto.

*5.4 Análisis por área o departamento*
- Tabla de áreas con nivel de riesgo promedio y dominios más afectados.
- Área(s) prioritaria(s) para intervención.

**6. Recomendaciones de intervención**
- Organizadas por nivel de urgencia (Inmediata / A mediano plazo / Preventiva).
- Cada recomendación cita el dominio o hallazgo que la origina.
- Tipos de intervención sugeridos (talleres, rediseño de procesos, canalizaciones
  individuales, seguimiento médico, actualización de política interna).
- Referencia al artículo 8 de la NOM-035 sobre las obligaciones del patrón
  según el nivel de riesgo detectado.

**7. Limitaciones del estudio**
- Sección estándar que aclara: los resultados reflejan la percepción de los
  trabajadores en el periodo evaluado, no constituyen diagnóstico clínico
  individual, y deben interpretarse en contexto organizacional.

**8. Espacio de validación**
- Nombre, firma, cédula profesional y fecha del psicólogo que revisó el reporte.
- Nota: "Este reporte fue generado por el sistema de cumplimiento NOM-035.
  La interpretación clínica y las recomendaciones fueron revisadas y validadas
  por el profesional firmante."

---

### Tareas de implementación

1. **Nuevo endpoint** `GET /api/v1/documentos/reporte-psicologico/?ciclo_id=X`
   - Agrega parámetro opcional `anonimo=true` para sustituir nombres por claves (T001, T002…).
   - Genera PDF con toda la estructura anterior.

2. **Plantilla HTML del reporte**
   - Tipografía formal (serif para el cuerpo del texto, sans para tablas).
   - Encabezado con logo de la empresa (si está configurado en el tenant).
   - Sección de firma con línea punteada y espacio para cédula.
   - Paginación con número de página y nombre del documento.

3. **Botón en la UI**
   - En la página de Resultados, junto al botón "Descargar PDF" existente:
     `[Reporte psicológico]` — solo habilitado si existen resultados calculados.
   - Modal previo con opción: "¿Incluir nombres o usar claves anónimas?"

4. **Textos de interpretación clínica** — ver sección siguiente.

#### Archivos
- `backend/documents/views.py` (nuevo endpoint)
- `backend/documents/templates/reporte_psicologico.html` (nueva plantilla)
- `frontend/src/pages/Resultados.jsx` (botón + modal de opciones)
- `frontend/src/services/resultados.js` (método `reportePsicologico`)

---

### Textos de interpretación clínica por dominio

> Fuente: NOM-035-STPS-2018 (DOF 23-oct-2018), definiciones del Apartado 4
> y Guía de Referencia III. Listos para usarse como constantes en el backend
> (`backend/documents/interpretaciones.py`) y renderizarse en el reporte.
> **Pendiente de visto bueno de psicólogos colaboradores antes de publicar.**

---

#### Guía I — Acontecimiento Traumático Severo

**Definición normativa (Apartado 4.4 NOM-035):**
"Aquél que puede amenazar la vida o la integridad física de una persona o de varias,
ante el que se experimenta miedo intenso, horror o sensación de desamparo,
y que genera en quien lo vive o lo presencia una respuesta de estrés severa."

**Texto de interpretación — caso positivo:**
"El trabajador reporta haber sido expuesto a un acontecimiento traumático severo
en el contexto laboral y presenta síntomas compatibles con una respuesta de estrés
postraumático, incluyendo recuerdos intrusivos, conductas de evitación o alteraciones
en el estado de alerta. Conforme al numeral 7.1 de la NOM-035-STPS-2018, el patrón
está obligado a canalizar a este trabajador para recibir atención médica y, en su
caso, psicológica. Este resultado no constituye un diagnóstico clínico; la evaluación
individual por un psicólogo clínico o psiquiatra es indispensable para determinar
la presencia o ausencia de Trastorno de Estrés Postraumático (TEPT) u otras
condiciones asociadas."

**Texto de interpretación — sin indicadores:**
"El trabajador no reporta exposición a acontecimientos traumáticos severos o,
habiéndola reportado, no presenta síntomas asociados que alcancen el umbral de
atención establecido por la norma. No se requiere canalización inmediata por
este instrumento."

---

#### Guía III — Interpretación por nivel de riesgo global

**Nivel Nulo (< 20 puntos)**
"La organización presenta una exposición nula o despreciable a factores de riesgo
psicosocial en el trabajo. Las condiciones laborales evaluadas no representan
una fuente de daño a la salud mental de los trabajadores en el ciclo evaluado.
Se recomienda mantener las prácticas actuales y aplicar el cuestionario en el
siguiente ciclo normativo para verificar continuidad."

**Nivel Bajo (20–44 puntos)**
"Se detecta una exposición baja a factores de riesgo psicosocial. Aunque no
representa un riesgo inmediato, existen áreas de mejora que, de no atenderse,
pueden escalar en ciclos posteriores. El patrón debe implementar acciones
preventivas enfocadas en los dominios con mayor puntaje, reforzar la comunicación
interna y revisar las condiciones identificadas en la siguiente evaluación anual."

**Nivel Medio (45–79 puntos)**
"Se detecta una exposición media a factores de riesgo psicosocial. Este nivel
indica que las condiciones de trabajo están generando tensión psicológica que
puede afectar el bienestar, la satisfacción laboral y la productividad de los
trabajadores. Conforme al Apartado 8 de la NOM-035-STPS-2018, el patrón debe
elaborar un plan de acción con medidas concretas, plazos definidos y responsables
asignados, orientadas a reducir los factores identificados como prioritarios."

**Nivel Alto (80–140 puntos)**
"Se detecta una exposición alta a factores de riesgo psicosocial. Las condiciones
laborales evaluadas representan una amenaza significativa para la salud mental
y física de los trabajadores, con riesgo de provocar o agravar trastornos de
ansiedad, depresión, agotamiento laboral (burnout) y trastornos musculoesqueléticos
de origen psicosocial. Se requieren acciones inmediatas: intervención organizacional
en los dominios críticos, seguimiento mensual del plan de acción, y evaluación
individual de los trabajadores con puntajes más elevados. El patrón debe notificar
a la Comisión de Seguridad e Higiene y registrar las acciones en el programa
de seguridad y salud en el trabajo."

**Nivel Muy Alto (> 140 puntos)**
"Se detecta una exposición muy alta a factores de riesgo psicosocial. Este nivel
constituye una situación crítica que requiere intervención urgente. La norma
establece que el patrón debe adoptar de inmediato medidas para controlar los
factores identificados, ofrecer atención médica y psicológica colectiva e individual,
y elaborar un programa de intervención con indicadores de seguimiento. La
persistencia de este nivel de exposición sin intervención puede derivar en daños
severos y permanentes a la salud de los trabajadores, así como en responsabilidades
legales para la organización conforme a la Ley Federal del Trabajo."

---

#### Guía III — Interpretación por dominio

**D1 — Condiciones en el ambiente de trabajo**
*Qué mide:* Presencia de condiciones físicas y materiales del entorno laboral que
pueden representar un riesgo para la seguridad o la comodidad del trabajador:
espacio, higiene, seguridad percibida, exposición a riesgos físicos y peligrosidad
de las actividades.

*Nivel Alto / Muy Alto:*
"Los trabajadores perciben que su entorno físico de trabajo representa un riesgo
para su integridad o salud. La exposición prolongada a condiciones ambientales
adversas activa de forma crónica el sistema de respuesta al estrés, incrementando
el riesgo de trastornos de ansiedad, insomnio y patologías musculoesqueléticas.
Se recomienda realizar una evaluación de riesgos físicos del centro de trabajo,
corregir las condiciones inseguras identificadas y comunicar a los trabajadores
las medidas adoptadas para reducir la percepción de peligro."

---

**D2 — Ritmo de trabajo**
*Qué mide:* Exigencias de velocidad en la ejecución de tareas: trabajar sin parar,
quedarse tiempo adicional y mantener un ritmo acelerado de forma habitual.

*Nivel Alto / Muy Alto:*
"El ritmo de trabajo impuesto supera la capacidad de recuperación fisiológica y
psicológica del trabajador. La bibliografía científica vincula el ritmo excesivo
con agotamiento laboral (burnout), fatiga crónica, errores operativos y accidentes.
Se recomienda revisar la carga de trabajo asignada, establecer pausas activas
reglamentadas y redistribuir tareas en periodos de alta demanda."

---

**D3 — Esfuerzo mental**
*Qué mide:* Demandas cognitivas del puesto: concentración sostenida, memorización
de información abundante, toma de decisiones bajo presión y atención simultánea
a múltiples tareas.

*Nivel Alto / Muy Alto:*
"Las demandas cognitivas del puesto exceden los recursos atencionales del trabajador
de forma habitual. La sobrecarga mental sostenida está asociada a deterioro de la
función ejecutiva, aumento de errores, fatiga mental, trastornos del sueño e
incremento del riesgo de trastornos ansiosos. Se recomienda revisar el diseño
del puesto, reducir la multitarea forzada, y proveer herramientas o apoyos
tecnológicos que reduzcan la carga cognitiva innecesaria."

---

**D4 — Actividades y responsabilidades**
*Qué mide:* Ambigüedad y conflicto de rol: recibir instrucciones contradictorias,
realizar actividades percibidas como innecesarias, y asumir responsabilidades
sobre resultados de otras personas.

*Nivel Alto / Muy Alto:*
"El trabajador experimenta ambigüedad y conflicto de rol de forma crónica. La falta
de claridad sobre las responsabilidades propias y la percepción de contradicción
en las instrucciones recibidas generan tensión psicológica constante, reducen
el sentido de eficacia personal y se asocian a mayor incidencia de ansiedad y
síntomas depresivos. Se recomienda revisar y comunicar con claridad las
descripciones de puesto, establecer canales únicos de instrucción y eliminar
duplicidad de mandos."

---

**D5 — Jornada de trabajo**
*Qué mide:* Extensión y gestión del tiempo de trabajo: horas extras frecuentes,
trabajo en días de descanso o festivos, y conflicto entre el tiempo dedicado
al trabajo y las responsabilidades familiares o personales.

*Nivel Alto / Muy Alto:*
"La jornada de trabajo está interfiriendo significativamente con la vida personal
y familiar del trabajador, configurando un conflicto trabajo-familia de alta
intensidad. Este factor es uno de los predictores más robustos de agotamiento
emocional, deterioro de la salud cardiovascular y trastornos del sueño en la
literatura de salud ocupacional. Se recomienda auditar las horas extra reales
trabajadas, implementar políticas de desconexión digital fuera del horario laboral
y revisar la dotación de personal en las áreas con mayor reporte de sobrecarga."

---

**D6 — Decisiones y autonomía en el trabajo**
*Qué mide:* Grado de control del trabajador sobre su propio ritmo, método y
organización de tareas, así como su capacidad de desarrollo y aspiración
profesional dentro del centro de trabajo.

*Nivel Alto / Muy Alto:*
"Los trabajadores perciben un bajo control sobre su trabajo, lo que según el
modelo Demanda-Control de Karasek constituye la combinación de mayor riesgo para
la salud cardiovascular y mental. La autonomía insuficiente limita la sensación
de competencia, reduce la motivación intrínseca y se asocia a mayor probabilidad
de desarrollar depresión laboral. Se recomienda revisar el diseño de puestos para
incorporar márgenes razonables de autonomía, establecer metas de desarrollo
profesional y socializar con los trabajadores las oportunidades de crecimiento
existentes en la organización."

---

**D7 — Cambios en el trabajo**
*Qué mide:* Frecuencia e impacto de los cambios organizacionales sobre la labor
del trabajador, y el grado en que sus ideas son tomadas en cuenta ante dichos cambios.

*Nivel Alto / Muy Alto:*
"Los trabajadores perciben que los cambios organizacionales los afectan
negativamente y que sus aportaciones no son consideradas. La incertidumbre ante
el cambio sin participación activa activa el sistema de amenaza y genera respuestas
de estrés crónico. Se recomienda implementar procesos de comunicación transparente
ante reestructuraciones, incluir a los trabajadores afectados en el diseño de
los cambios y proveer acompañamiento durante las transiciones."

---

**D8 — Capacitación**
*Qué mide:* Claridad en las funciones y objetivos del puesto, acceso a capacitación
útil y pertinente, y disponibilidad de información para resolver problemas laborales.

*Nivel Alto / Muy Alto:*
"Los trabajadores reportan déficit de capacitación y de información para el
desempeño de su puesto. La falta de habilidades percibidas para afrontar las
demandas del trabajo es un factor de riesgo conocido para el desarrollo de
estrés laboral crónico y síndrome de agotamiento. Se recomienda realizar un
diagnóstico de necesidades de capacitación, implementar un programa de inducción
y formación continua, y asegurar que los trabajadores cuenten con acceso oportuno
a la información necesaria para su función."

---

**D9 — Liderazgo y subordinación**
*Qué mide:* Calidad de la relación con el jefe inmediato: apoyo para organizar el
trabajo, comunicación oportuna, valoración de las opiniones del trabajador y
orientación para la resolución de problemas.

*Nivel Alto / Muy Alto:*
"La relación con el liderazgo inmediato es percibida como deficiente en apoyo,
comunicación y reconocimiento. El liderazgo de baja calidad es uno de los factores
de riesgo psicosocial con mayor impacto documentado sobre la salud mental de los
equipos de trabajo, asociado a mayor prevalencia de burnout, rotación de personal
y ausentismo. Se recomienda implementar un programa de desarrollo de habilidades
de liderazgo para mandos medios y superiores, con énfasis en comunicación efectiva,
retroalimentación constructiva y gestión del clima laboral."

---

**D10 — Relaciones con los compañeros**
*Qué mide:* Calidad del vínculo con los pares: confianza, resolución respetuosa
de conflictos, sentido de pertenencia, colaboración y apoyo entre compañeros.

*Nivel Alto / Muy Alto:*
"El ambiente de relaciones interpersonales entre compañeros es percibido como
deteriorado. Las relaciones laborales de baja calidad reducen el apoyo social
percibido, que es uno de los amortiguadores más importantes frente al estrés
laboral. Su deterioro se asocia a mayor aislamiento, conflictos interpersonales,
conductas de exclusión y mayor vulnerabilidad individual a trastornos del estado
de ánimo. Se recomienda implementar actividades de integración de equipos,
establecer protocolos claros de resolución de conflictos y revisar si existen
situaciones de hostigamiento no reportadas formalmente."

---

**D11 — Rendimiento y reconocimiento**
*Qué mide:* Percepción de justicia en la evaluación del desempeño, oportunidades
de crecimiento, pago puntual y justo, reconocimiento por resultados, estabilidad
del empleo y orgullo/compromiso organizacional.

*Nivel Alto / Muy Alto:*
"Los trabajadores perciben que su desempeño no es reconocido de forma justa,
que las oportunidades de crecimiento son limitadas y que la estabilidad de su
empleo es incierta. La percepción de injusticia organizacional es un predictor
robusto de síntomas depresivos, agotamiento emocional y conductas
contraproducentes. Se recomienda revisar los sistemas de evaluación de desempeño
para asegurar su transparencia y equidad, comunicar con claridad las políticas
de compensación y crecimiento, y reforzar acciones de reconocimiento formal
e informal."

---

**D12 — Violencia laboral**
*Qué mide:* Exposición a actos de violencia psicológica en el trabajo: críticas
destructivas, burlas, humillaciones, exclusión deliberada, manipulación,
apropiación de logros ajenos, bloqueo de ascensos y presencia de violencia
en el entorno laboral.

*Nivel Alto / Muy Alto:*
"Se detecta una exposición significativa a actos de violencia psicológica en el
trabajo. La violencia laboral de tipo psicológico —también denominada mobbing o
acoso laboral— produce daños severos y progresivos en la salud mental del
trabajador: ansiedad, depresión, trastorno de estrés postraumático, baja autoestima
y deterioro de la identidad profesional. Conforme al numeral 7 de la NOM-035-STPS-2018,
el patrón tiene la obligación de establecer y difundir en el centro de trabajo
una política de prevención de violencia laboral, así como adoptar medidas para
prevenir y atender las prácticas opuestas al entorno organizacional favorable.
Se recomienda activar de forma inmediata el protocolo de atención a casos de
violencia, garantizar la confidencialidad de los reportes y proveer acompañamiento
psicológico a las personas afectadas."

---

**D13 — Atención a clientes y usuarios**
*Qué mide:* Exigencias emocionales específicas de los puestos que implican trato
directo con clientes o usuarios: atender personas enojadas, en situación de
vulnerabilidad o de violencia, y la necesidad de gestionar emociones propias
en beneficio del servicio (trabajo emocional).

*Nivel Alto / Muy Alto:*
"Los trabajadores en contacto directo con clientes están experimentando una carga
emocional elevada derivada de su trabajo. La supresión crónica de emociones propias
para mantener la actitud de servicio requerida (trabajo emocional de superficie)
es un factor de riesgo específico para el agotamiento emocional y el síndrome
de burnout, especialmente en servicios de salud, atención a personas vulnerables
y puestos de atención a clientes conflictivos. Se recomienda implementar supervisión
psicológica periódica para estos puestos, establecer protocolos de desescalada
ante situaciones de violencia con clientes y proveer espacios de recuperación
emocional entre turnos de atención."

---

**D14 — Actitudes de las personas supervisadas**
*Qué mide:* Dificultades específicas que enfrentan los supervisores derivadas
de las actitudes de sus subordinados: falta de comunicación oportuna, obstaculización
de resultados, poca cooperación e ignorancia de sugerencias de mejora.

*Nivel Alto / Muy Alto:*
"Los supervisores y jefes de área reportan dificultades significativas relacionadas
con las actitudes de las personas que supervisan. Esta situación genera en el
supervisor una tensión de rol específica: la responsabilidad sobre resultados que
dependen de terceros, combinada con la percepción de falta de control sobre el
desempeño del equipo, incrementa el riesgo de agotamiento laboral en mandos medios.
Se recomienda revisar los procesos de comunicación ascendente y descendente en los
equipos, identificar si las actitudes reportadas tienen origen en problemas de
clima organizacional más amplios, y proveer a los supervisores herramientas de
gestión de equipos y resolución de conflictos."
