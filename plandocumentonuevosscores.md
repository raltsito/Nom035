# Plan — Corrección de metodología Guía III en el dashboard (scoring.py)

**Estado: ✅ AUTORIZADO E IMPLEMENTADO (2026-07-13).** Dirección autorizó el
cambio; implementación y verificación completas (ver commit correspondiente).
Pendiente: recalcular ciclo por ciclo en producción tras el deploy (manual,
con el botón "Calcular diagnóstico"), y decidir el aviso a plantas/clientes
sobre el cambio de categorías (sección 3, sin resolver).

Durante la implementación se ampliaron el alcance y hallazgos respecto a lo
documentado abajo: también se corrigió `backend/documents/` (informes
DOCX/Excel, que tenía su propia agrupación de dominios no oficial y el mismo
bug de cortes), y se encontró y corrigió un bug independiente en Guía I
(criterio de atención clínica: era una suma combinada D2+D3+D4≥2 cuando el
oficial es D2≥1 O D3≥3 O D4≥2 por sección — afectaba a 5 de 1,739
trabajadores reales, siempre como falso positivo).

## 1. Qué se descubrió (contexto, no repetir la investigación)

Comparando `backend/m06_results/scoring.py` (usado por el dashboard `/resultados`
en producción) contra `generar_informe.py` (script local que ya usa la
metodología oficial de la Guía de Referencia III, validada con el cliente el
2026-07-07), se encontraron 3 problemas independientes, todos en el cálculo de
Guía III:

1. **Cortes globales (Cfinal) desactualizados.** `scoring.py:31-36` usa
   `20/45/80/141`; lo oficial es `50/75/99/140` (`generar_informe.py:502`,
   `_CORTES_FINAL`).
2. **Agrupación de dominios no oficial.** `scoring.py` califica los 14 bloques
   crudos del cuestionario (D1-D14) cada uno con su propio corte inventado.
   Lo oficial son 5 categorías y 10 dominios (`_CATEGORIA_DOMINIOS`,
   `_CORTES_CATEGORIA`, `_CORTES_DOMINIO` en `generar_informe.py:504-556`),
   con reglas de reagrupación (`_dominio_oficial()` en `generar_informe.py:605`):
   - D5 → se separa en "Jornada de trabajo" (preg. 1-2) e "Interferencia
     trabajo-familia" (preg. 3-6)
   - D8 → se separa en "Liderazgo" (preg. 1-4) y "Falta de control sobre el
     trabajo" (preg. 5-6)
   - D11 → se separa en "Reconocimiento del desempeño" (preg. 1-6) e
     "Insuficiente sentido de pertenencia e inestabilidad" (preg. 7-10)
   - D13 → suma a "Carga de trabajo"; D14 → suma a "Relaciones en el trabajo"
3. **3 preguntas con `Pregunta.inversa` mal marcado en la BD.** Verificado
   contra la Tabla 5 de la Guía III (`_GUIA_III_INVERSOS` en
   `generar_informe.py:569`):
   - D1-P1 (ítem 1): debería invertirse, en BD `inversa=False`
   - D1-P4 (ítem 4): debería invertirse, en BD `inversa=False`
   - D7-P1 (ítem 29): NO debería invertirse, en BD `inversa=True`

**Impacto medido en datos reales** (`nom035_local`, 1,054 resultados de Guía
III, excluyendo tenant PRUEBA): **68.8% cambia de categoría** al aplicar los
cortes oficiales, siempre hacia menor riesgo (Medio→Bajo: 278, Bajo→Nulo: 231,
Alto→Medio: 166, Medio→Nulo: 49). Plantas más afectadas: Silao (239), Saltillo
(178), San Luis (178). El dashboard actual sobreestima el riesgo
sistemáticamente. Detalle completo en el DOCX enviado a Dirección.

**Nota:** el punto 3 (preguntas invertidas) afecta el `puntaje_total` mismo,
no solo la categoría — es un bug más profundo que los cortes. El 68.8% medido
arriba es solo el efecto de los cortes; el efecto de las 3 preguntas no se
cuantificó por separado (ver sección 4, pendiente).

## 2. Archivos que hay que tocar cuando se autorice

- [ ] `backend/m06_results/scoring.py`
  - [ ] Reemplazar `GUIA_III_GLOBAL` por los cortes oficiales `_CORTES_FINAL`
  - [ ] Reemplazar `GUIA_III_DOMINIOS` (por bloque D1-D14) por el cálculo
    oficial: reagrupar preguntas en los 10 dominios oficiales antes de sumar,
    usando la misma lógica que `_dominio_oficial()` de `generar_informe.py`
  - [ ] Decidir si se agrega también el nivel intermedio de "categoría"
    (`_CORTES_CATEGORIA`, 5 grupos) al resultado guardado, o si por ahora solo
    se corrigen dominio + global (ver sección 3, decisión pendiente)
  - [ ] Corregir la inversión de las 3 preguntas — **decidir cómo**: ¿arreglar
    el dato `Pregunta.inversa` en la BD (migración de datos) o ignorar ese
    campo para Guía III y usar una tabla de ítems fija como hace
    `generar_informe.py` (más robusto, no depende de que el dato en BD esté
    bien)? Recomendado: tabla fija, igual que el script local.
- [ ] Migración de datos (si se decide corregir `Pregunta.inversa` en vez de
  usar tabla fija) para las 3 preguntas identificadas arriba.
- [ ] `backend/m06_results/models.py` — revisar si `ResultadoDominio` necesita
  un campo nuevo para el nivel de "categoría" (5 grupos) si se decide
  guardarlo, o si con dominio (10) + global basta para el dashboard actual.
- [ ] Frontend (`frontend/src/pages/Resultados.jsx`,
  `ResultadosDashboard` y componentes de dominio/heatmap) — revisar si asumen
  los 14 dominios D1-D14 en algún lado (labels, orden, mapa de calor) y
  necesitan ajuste a los 10 dominios oficiales.
- [ ] Guía I — **no se tocó en esta investigación**, no se encontró evidencia
  de que tenga el mismo problema. Confirmar que sigue igual (criterio
  binario D1≥1 y D2+D3+D4≥2, ver `scoring.py:117-118`) antes de tocar nada ahí.

## 3. Decisiones a tomar antes de programar (no asumir, preguntar)

- ¿Se recalculan TODOS los ciclos históricos automáticamente al desplegar, o
  se corre `Calcular diagnóstico` manualmente ciclo por ciclo? (Hay un botón
  ya existente en `/resultados` que llama a `POST /resultados/calcular/`.)
- ¿Se avisa a las plantas/clientes de que el dashboard va a cambiar de
  categoría para resultados que ya vieron? Sobre todo las más afectadas
  (Silao, Saltillo, San Luis).
- ¿Guardamos el nivel de "categoría" (5 grupos oficiales, intermedio entre
  dominio y global) en el modelo, o el dashboard se queda solo con dominio +
  global como hasta ahora?

## 4. Pendiente de investigar (no se alcanzó a hacer)

- [ ] Cuantificar el impacto de las 3 preguntas mal invertidas por separado
  (cuánto cambia `puntaje_total` en los trabajadores que respondieron esos
  ítems con valor ≠ 2, que es donde la inversión sí cambia el resultado).
- [ ] Revisar si Guía I tiene algún problema similar (no se auditó a fondo,
  solo se confirmó que el criterio binario coincide en ambos lados).
- [ ] Revisar `documents/views.py::_build_tasas_respuesta` y demás lugares que
  lean `ResultadoAplicacion.categoria` para confirmar que no haya más
  consumidores del dato que necesiten ajuste además del dashboard.

## 5. Cómo verificar el fix localmente (una vez implementado)

Repetir el setup que se usó para la investigación:

1. Levantar backend apuntando a `nom035_local` (tiene datos reales de
   producción, restaurados vía dump — ver memoria `reference-railway-db-dump`):
   ```
   DJANGO_SETTINGS_MODULE=intra_nom035.settings.development
   DATABASE_URL=postgres://postgres:carl32928@localhost:5432/nom035_local
   ```
   Verificar migraciones pendientes primero (`python manage.py showmigrations`)
   — al hacer esta investigación faltaban `accounts.0003_user_cedula_profesional`
   y `documents.0001_initial`.
2. Correr `compara_cortes.py` (ver historial de conversación / recrear si se
   perdió) contra `nom035_local` para confirmar que el % de discrepancia baja
   a 0% después del fix.
3. Levantar frontend (`npm run dev`), entrar como super admin (usuario
   `ORBITA`, tenant None → puede ver cualquier planta) y revisar visualmente
   `/resultados` para Silao (la más afectada) antes/después.
4. Confirmar que `POST /resultados/calcular/` recalcula correctamente y que
   la "Distribución de riesgo" y el "Mapa de calor por dominio" reflejan los
   nuevos números.

## 6. Documento ya enviado

`Solicitud_Autorizacion_Correccion_Guia_III.docx` (raíz del repo) — enviado a
Dirección para autorización. Contiene el resumen ejecutivo, tablas antes/después,
evidencia cuantitativa y casilla de firma. **No aplicar el cambio hasta tener
ese documento firmado o una autorización explícita por otro medio.**
