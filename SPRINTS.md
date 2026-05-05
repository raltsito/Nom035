# Plan de Sprints — Intra NOM-035

## Sprint 1 — Nuevo modelo de links por guía ✅ COMPLETADO

**Objetivo:** En lugar de un link por trabajador, 3 links compartidos fijos (uno por guía).

### Cambios realizados
- [x] Nuevo modelo `GuiaLink(ciclo, cuestionario, token, activo)` en `m05_questionnaires/models.py`
- [x] Migración `0002_guialink.py` aplicada
- [x] Endpoint admin `POST /api/guia-links/crear-links/` — crea los 3 links para un ciclo
- [x] Endpoint admin `GET /api/guia-links/?ciclo_id=X` — lista los links del ciclo
- [x] Endpoint público `GET /api/publica/guia/<token>/` — punto de entrada para trabajadores
- [x] Eliminado `crear_masivo` (seleccionaba 1 guía por tamaño de empresa)
- [x] Frontend: sección "Links de Guías" en `/cuestionarios` con botón Generar y 3 tarjetas con URL + Copiar
- [x] Fix bug crítico en `api.js`: refresh de tokens guardaba `"undefined"` y no rotaba el refresh token

---

## Sprint 2 — Flujo de identificación por número de trabajador ✅ COMPLETADO

**Objetivo:** Al abrir el link compartido, el trabajador se identifica antes de ver el cuestionario.

### Cambios realizados
- [x] Endpoint `POST /api/publica/guia/<token>/identificar/` — valida `num_empleado`, devuelve nombre para confirmación
- [x] Endpoint `POST /api/publica/guia/<token>/confirmar/` — confirma identidad, crea/recupera `Aplicacion`, devuelve token
- [x] Pantalla pública `/guia/:token` — paso 1: ingresa número de trabajador
- [x] Pantalla de confirmación — "¿Eres Juan Pérez García?" con botones "No soy yo" / "Sí, soy yo"
- [x] Al confirmar: redirige automáticamente a `/responder/<aplicacion_token>`
- [x] Ruta `/guia/:token` registrada en `App.jsx`

---

## Sprint 3 — Lógica secuencial V → III → I ✅ COMPLETADO

**Objetivo:** Un trabajador no puede contestar la Guía III sin completar la V, ni la I sin completar la III.

### Cambios realizados
- [x] Validación en `confirmar_trabajador`: si la guía requiere una previa, verifica que exista una `Aplicacion` completada
- [x] Responde 403 con `{ bloqueado: true, guia_requerida, mensaje }` si no se cumple el requisito
- [x] Frontend: pantalla de bloqueo con diagrama visual V → III → I mostrando cuál debe completarse primero
- [x] Botón "Volver" para reintentar con otro número o guía

---

## Sprint 4 — Actualización del panel admin ✅ COMPLETADO

**Objetivo:** El admin ve y gestiona 3 links fijos en lugar de uno por trabajador.

### Cambios realizados
- [x] Endpoint `GET /api/aplicaciones/progreso/?ciclo_id=X` — devuelve todos los trabajadores con estado por guía (V, III, I)
- [x] Tabla de progreso: columnas Guía V, Guía III, Guía I con chips de estado por trabajador
- [x] Stats actualizadas: Completos / En progreso / Sin iniciar
- [x] Botón limpiar por trabajador (limpia todas sus guías del ciclo)
- [x] Filtro por ciclo

---

## Sprint 5 — Reportes y exportaciones actualizadas ✅ COMPLETADO

**Objetivo:** Los reportes reflejan las 3 guías por trabajador.

### Cambios realizados
- [x] Endpoint `GET /api/aplicaciones/exportar/?ciclo_id=X` — genera CSV con progreso por guía
- [x] CSV con columnas `num_empleado`, `nombre`, `area`, `puesto`, `guia_V`, `guia_III`, `guia_I`
- [x] Estados exportados por guía: `completado`, `en_progreso`, `pendiente` o `sin_iniciar`
- [x] Frontend: botón "Exportar Excel" junto al selector de ciclo en `/cuestionarios`
- [x] Servicio `aplicacionesService.exportar` con descarga como archivo CSV
- [x] Exportación Excel `.xlsx` estilizada con encabezado, autofiltro, bordes, colores y estados resaltados
- [x] No se encontraron gráficas que ajustar en la página de cuestionarios

---

## Sprint 6 - Cuestionarios oficiales, condicionales y scoring COMPLETADO

**Objetivo:** Actualizar las guias desde el PDF actualizado y recalcular resultados con las reglas correctas.

### Cambios realizados
- [x] Guia V actualizada como datos del trabajador con 15 campos de captura
- [x] Guia I actualizada con 20 preguntas si/no y condicionales por acontecimiento traumatico
- [x] Guia III actualizada con 74 preguntas: 64 base, 2 preguntas condicionales y 8 preguntas dependientes
- [x] Soporte backend para tipos de respuesta `frecuencia`, `si_no`, `texto` y `opcion`
- [x] Soporte backend y frontend para preguntas condicionales con operador `any` / `all`
- [x] Seed actualizado para crear, actualizar y limpiar preguntas/dominios obsoletos
- [x] Calculo de resultados actualizado para Guia I y Guia III
- [x] Guia V omitida del diagnostico de riesgo porque solo captura datos del trabajador
- [x] Dashboard de resultados actualizado para categoria `nulo`, ademas de `bajo`, `medio`, `alto` y `muy_alto`
