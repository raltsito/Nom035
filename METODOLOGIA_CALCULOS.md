# Metodología y fórmulas de cálculo — NOM-035-STPS-2018

Documento de referencia de **todas** las fórmulas que el sistema usa para calificar
cuestionarios individuales y para agregar resultados a nivel centro de trabajo /
área. Fuente normativa: Guía de Referencia I, III y V de la NOM-035-STPS-2018
(DOF 23-oct-2018), validada contra datos reales de LEAR el 2026-07-07.

El motor de cálculo vive en un solo lugar (`backend/m06_results/scoring.py`) y se
ejecuta una vez por `Aplicacion` (un trabajador respondiendo un cuestionario). Los
reportes (dashboard, DOCX, PDF) **no recalculan** nada: solo agregan los
`ResultadoAplicacion` / `ResultadoDominio` / `ResultadoDominioOficial` ya
guardados en BD.

```
Trabajador responde cuestionario
        │
        ▼
m06_results/scoring.py  →  calcula puntaje individual (Guía I o III)
        │
        ▼
ResultadoAplicacion / ResultadoDominio / ResultadoDominioOficial (BD)
        │
        ▼
backend/documents/views.py  →  agrega (promedios, %, rankings) para el informe
        │
        ▼
backend/documents/docx_builder.py  →  arma el DOCX final
```

---

## 1. Archivos involucrados

| Archivo | Rol |
|---|---|
| `backend/m06_results/scoring.py` | **Motor de calificación individual.** Guía I y Guía III. Única fuente de verdad de los cortes oficiales. |
| `backend/m06_results/models.py` | Guarda el resultado calculado (`ResultadoAplicacion`, `ResultadoDominio`, `ResultadoDominioOficial`). |
| `backend/documents/views.py` | Agregación a nivel centro de trabajo/ciclo: promedios, % por nivel de riesgo, ranking por área, tamaño de muestra estadístico. |
| `backend/documents/docx_builder.py` | Vuelca el contexto agregado al DOCX (tablas, gráficas, texto). |
| `backend/documents/interpretaciones.py` | Texto clínico/recomendaciones por dominio y nivel (no numérico). |
| `backend/documents/contenido_normativo.py` | Recomendaciones extensas por dominio oficial (no numérico). |
| `backend/m00_onboarding/views.py` (`_muestra`, `_estrato`) | Fórmula de tamaño de muestra (Ecuación 1) y estratificación proporcional. |
| `generar_informe.py` (raíz del repo) | Script local histórico del que se **portó** la lógica de `scoring.py`. Ya no es la fuente de verdad en producción, pero documenta el origen y validación manual contra el cliente. |

---

## 2. Guía I — Acontecimiento Traumático Severo (ATS)

Cuestionario de 4 secciones (D1-D4). Resultado **binario**, no hay niveles de
riesgo por puntaje.

- **D1 (Sección I — Acontecimiento):** cuenta respuestas "Sí" (`valor == 1`).
  `hay_acontecimiento = puntaje_D1 >= 1`.
- **D2, D3, D4 (Secciones II, III, IV):** cada una suma sus "Sí" **por
  separado** (no se combinan en un solo total).

**Fórmula de decisión** (Guía I, apartado GR.I inciso b):

```
requiere_atencion =  D1 ≥ 1
                  AND (D2 ≥ 1  OR  D3 ≥ 3  OR  D4 ≥ 2)
```

Importante: **no** es una suma D2+D3+D4 contra un umbral combinado — cada
sección tiene su propio corte independiente. Esto fue una fuente real de
confusión y quedó documentado explícitamente en el código
(`backend/m06_results/scoring.py:204-213`) tras validarlo con el cliente.

Categoría resultante: `'requiere_atencion'` o `'sin_indicadores'`.

---

## 3. Guía III — Factores de riesgo psicosocial

Cuestionario de 72 ítems tipo Likert (frecuencia 0-4), organizado en el
sistema en **14 bloques de captura** (D1-D14), que la Guía de Referencia III
reagrupa oficialmente en **10 dominios** → **5 categorías** → **1 calificación
global** (Tabla 6, "Cuadro de puntajes").

### 3.1 Inversión de ítems

Algunos ítems están redactados en sentido inverso (a mayor frecuencia, menor
riesgo) y su puntaje se invierte antes de sumar:

```
valor_final = (4 - valor_respuesta)   si el ítem es "inverso"
            = valor_respuesta         si no
```

La tabla de qué ítems son inversos es la **Tabla 5 oficial de la Guía III**,
codificada por número de ítem 1-72 en `_GUIA_III_INVERSOS` /
`_GUIA_III_ITEM_OFFSET` (`scoring.py:107-122`). **No** se usa el campo
`Pregunta.inversa` de la BD para Guía III porque se detectaron 3 ítems mal
marcados ahí; el número de ítem oficial es la fuente de verdad.

### 3.2 Jerarquía de agregación (suma simple, sin promedios ni %)

```
Ítem (0-4, ya invertido si aplica)
   ↓ suma
Dominio oficial (10)         ← Tabla 6
   ↓ suma
Categoría (5)                 ← Tabla 6
   ↓ suma
Calificación global (Cfinal)
```

Todo es **suma de puntos crudos** — la NOM-035 no usa porcentajes para
clasificar, solo para el indicador interno referencial por bloque (ver 3.4).

Dos casos especiales de reagrupación (un bloque de captura se reparte entre
dos dominios oficiales según el número de pregunta):

- **D5** → preguntas 1-2: "Jornada de trabajo"; preguntas 3+: "Interferencia
  trabajo-familia".
- **D8** → preguntas 1-4: "Liderazgo"; preguntas 5+: "Falta de control sobre
  el trabajo".
- **D11** → preguntas 1-6: "Reconocimiento del desempeño"; preguntas 7+:
  "Insuficiente sentido de pertenencia e inestabilidad".

D13 (cargas emocionales, filtro "atiendo clientes") y D14 (supervisión de
personal, filtro "soy jefe/supervisor") son **condicionales**: si el
trabajador contesta "No" al filtro, el bloque completo se marca 0/0 y **no**
entra a ningún promedio ni suma.

### 3.3 Cortes oficiales por nivel (Tabla 6)

Cada nivel (`nulo` / `bajo` / `medio` / `alto` / `muy_alto`) se determina por
**rangos de suma** (límite superior exclusivo), específicos por dominio,
categoría y global. Ejemplos (ver la tabla completa en
`scoring.py:46-67`):

- **Calificación global (Cfinal):** nulo `<50`, bajo `<75`, medio `<99`, alto
  `<140`, muy alto `≥140`.
- **Categoría "Entorno organizacional":** nulo `<10`, bajo `<14`, medio `<18`,
  alto `<23`, muy alto `≥23`.
- **Dominio "Violencia":** nulo `<7`, bajo `<10`, medio `<13`, alto `<16`, muy
  alto `≥16`.

### 3.4 Indicador referencial de los 14 bloques crudos (no oficial)

Para mostrar un semáforo por bloque de captura (que no es la unidad oficial
de calificación), se usa un **corte porcentual** genérico, solo informativo:

```
% del bloque = puntaje_bloque / puntaje_max_bloque * 100
nivel = nulo <20% | bajo <45% | medio <60% | alto <75% | muy_alto ≥75%
```

Esto **no sustituye** el resultado oficial por dominio/categoría/global de
la sección 3.3 — es un apoyo visual interno (`_CUTOFFS_PCT`, `scoring.py:105`).

---

## 4. Guía V — Datos del trabajador

No genera resultado de riesgo. `calcular_resultado()` retorna `None` para
esta guía; solo alimenta datos demográficos (edad, sexo, antigüedad, área,
puesto) usados en la agregación.

---

## 5. Agregación a nivel centro de trabajo (informe DOCX/PDF)

Todo en `backend/documents/views.py`, sobre los resultados individuales ya
calculados (no se re-lee ninguna respuesta cruda). Fórmulas relevantes:

- **Nivel de riesgo global de la organización (corregido, auditoría 2026-07):**
  ```
  nivel_global    = MODA de los niveles individuales (nivel predominante)
  promedio_global = round( Σ puntaje_total_individual / n_validos )   ← SOLO descriptivo
  ```
  **PROHIBIDO** clasificar el promedio con los cortes de Cfinal: los puntos de
  corte de la Tabla 6 aplican a cuestionarios individuales. La conclusión
  organizacional se basa en la distribución (moda, % en medio+, % en alto+muy
  alto, mediana), y todo promedio se acompaña de la nota: *"El puntaje promedio
  es un estadístico descriptivo y no constituye un nivel de riesgo oficial del
  centro de trabajo conforme a la NOM-035-STPS-2018."* Lo mismo aplica a
  grupos (área, sexo, edad, puesto, jornada): distribuciones, nunca promedios
  clasificados; grupos con n < umbral (5 por defecto) se reservan por
  confidencialidad.
- **Distribución poblacional por nivel:** conteo y `%` de trabajadores en
  cada una de las 5 categorías (`nulo…muy_alto`), sobre el total con Guía III
  completada.
- **Por categoría/dominio oficial (agregado poblacional):** reclasifica a
  *cada trabajador* con los cortes oficiales de la Tabla 6 aplicados a su
  propio puntaje por dominio/categoría, y agrega:
  - `pct_promedio` = promedio de los % individuales (solo descriptivo, no
    clasifica nada).
  - `categoria_predominante` = moda de las 5 categorías entre trabajadores.
  - `pct_intervencion` = `% de trabajadores en alto + muy_alto` (define
    prioridad de las recomendaciones).
  - `pct_accion` = `% de trabajadores en medio + alto + muy_alto`.
- **Ranking de categorías/dominios para "Conclusiones":** ordenado por
  `pct_intervencion` desc, desempate por `pct_accion` desc — el dominio con
  mayor urgencia aparece primero.
- **Análisis por área:** distribución de niveles individuales por área
  (moda, % alto+muy alto, promedio solo descriptivo), ordenado por
  % alto+muy alto. Áreas con n < umbral de confidencialidad → "Dato
  reservado por confidencialidad".
- **Tasa de respuesta / % completado:** `completadas / aplicadas * 100`.

---

## 6. Tamaño de muestra estadístico (Ecuación 1, NOM-035)

Cuando el centro de trabajo tiene más de 50 (o el umbral que aplique)
trabajadores, la norma permite evaluar una muestra representativa en vez del
100%. Fórmula con población finita, IC 95%, `Z = 1.96`, `p = q = 0.5`,
error `e = 5%` (`backend/m00_onboarding/views.py:28-31`):

```
n = (Z² · p · q · N) / (e² · (N − 1) + Z² · p · q)
  = (0.9604 · N) / (0.0025 · (N − 1) + 0.9604)
```

La estratificación proporcional por subgrupo (p. ej. por sexo o área) usa el
**método de restos mayores** (`_estratos_restos_mayores`,
`backend/m00_onboarding/views.py`), que conserva el total exacto:

```
1. cuota_e = (N_estrato / N_total) · n          (cuota exacta)
2. asignado_e = parte entera de cuota_e
3. los lugares restantes (n − Σ asignado) se reparten por fracción mayor
4. Σ asignado == n  (verificado por pruebas)
```

Nota: aplicar `ceil` a cada estrato (método anterior) hacía que la suma
excediera n; se conserva `_estrato` solo como cuota mínima de referencia. La
proporcionalidad por sexo exigida por GR.III III.1 se verifica con este
reparto.

---

## 7. Notas de validación / puntos que fueron fuente de error

- **Guía I:** el umbral es por sección independiente (D2≥1 O D3≥3 O D4≥2),
  no una suma combinada — confirmado con el cliente tras un desajuste inicial.
- **Guía III, inversión de ítems:** el campo `Pregunta.inversa` en BD no es
  confiable (3 ítems mal marcados); la inversión se calcula siempre desde la
  tabla fija de números de ítem oficiales (Tabla 5).
- **Guía III, D13/D14:** solo se califican si el trabajador contestó "Sí" a
  la pregunta filtro; si no, cuentan 0/0 y no distorsionan el promedio.
- **Los 14 bloques de captura ≠ los 10 dominios oficiales ≠ las 25
  dimensiones:** el sistema guarda todo (`ResultadoDominio` = bloques de
  captura, semáforo referencial no normativo; `ResultadoDominioOficial` = 10
  dominios Tabla 6 con nivel oficial; `ResultadoCategoria` = 5 categorías
  oficiales; `ResultadoDimension` = 25 dimensiones Tabla 6, SOLO descriptivas
  — la NOM no define cortes por dimensión).

## 8. Validación y trazabilidad (motor v2, auditoría 2026-07)

- **Ningún faltante se convierte en 0.** Un reactivo obligatorio sin
  respuesta, un valor fuera de 0-4 o un filtro sin responder dejan el
  cuestionario en `estatus_validacion='requiere_revision'` y NO se clasifica
  (`categoria='sin_calificar'`); queda fuera de todas las distribuciones.
- **Reactivos condicionados:** 65-68 solo aplican con filtro "atiende
  clientes"=Sí; 69-72 con "es jefe"=Sí. Filtro "Sí" + condicionado faltante →
  incompleto. Filtro "No" + condicionados contestados → advertencia
  registrada (no suman). Filtro faltante → incompleto.
- **Trazabilidad:** cada `ResultadoAplicacion` guarda `version_motor`,
  `hash_respuestas` (SHA-256) y `detalle` (validación estructurada, secciones
  ATS, filtros). El recálculo es idempotente y transaccional.
- **Guía I:** se persisten los conteos por sección y qué criterio (II/III/IV)
  disparó la valoración clínica (`detalle.guia_i`).
- La fuente normativa se verificó contra el PDF oficial de la STPS
  (DOF 23-oct-2018) el 2026-07-14 — ver
  `docs/auditoria_metodologica_nom035.md`.
