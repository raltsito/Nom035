# Plan de Sprints - Correos de recordatorio

## Objetivo general

Agregar correo electronico al alta de trabajadores y permitir que el administrador envie recordatorios a trabajadores pendientes. El sistema debe detectar automaticamente que guia le falta a cada trabajador y enviarle solo el link correspondiente.

## Regla de envio por trabajador

El flujo de guias se mantiene en orden:

1. Guia V
2. Guia III
3. Guia I

La guia enviada depende del avance del trabajador en el ciclo seleccionado:

- Si no ha completado Guia V: enviar link de Guia V.
- Si ya completo Guia V pero no Guia III: enviar link de Guia III.
- Si ya completo Guia III pero no Guia I: enviar link de Guia I.
- Si ya completo Guia V, Guia III y Guia I: no enviar correo.

Ejemplos:

- Miguel Angel ya contesto Guia V: se le envia solo el link de Guia III.
- Carlos Alberto ya contesto Guia III: se le envia solo el link de Guia I.
- Un trabajador sin ninguna guia completada: se le envia solo el link de Guia V.

---

## Sprint 1 - Correo en trabajadores COMPLETADO

**Objetivo:** Guardar correo electronico por trabajador.

### Backend
- [x] Campo `email` confirmado en el modelo `Trabajador`.
- [x] Correo marcado como obligatorio para nuevos trabajadores.
- [x] Migracion de ajuste del campo generada y aplicada.
- [x] Actualizar serializers de trabajadores para aceptar y devolver correo.
- [x] Validar formato de correo.
- [x] Definir correo como obligatorio.

### Frontend
- [x] Agregar campo de correo al formulario de alta de trabajador.
- [x] Mostrar correo en la tabla/listado de trabajadores.
- [x] Mostrar error claro si el correo no tiene formato valido.

### Pruebas esperadas
- [x] Crear trabajador con correo valido.
- [x] Editar correo de trabajador existente.
- [x] Confirmar que el correo se conserva en base de datos.

---

## Sprint 2 - Deteccion de guia pendiente COMPLETADO

**Objetivo:** Calcular que guia le falta a cada trabajador por ciclo.

### Backend
- [x] Crear helper para obtener la siguiente guia pendiente de un trabajador en un ciclo.
- [x] Reutilizar el orden oficial V -> III -> I.
- [x] Considerar solo aplicaciones con estado `completado` como guias terminadas.
- [x] Si no existe aplicacion o esta `pendiente` / `en_progreso`, considerar esa guia como pendiente.
- [x] Si ya completo las 3 guias, devolver `null` o equivalente.
- [x] Reutilizar la misma logica en la confirmacion publica de trabajadores.
- [x] Agregar helper de lote para el futuro envio masivo de correos.

### Casos esperados
- [x] Sin guias completadas -> pendiente Guia V.
- [x] Guia V en progreso -> pendiente Guia V.
- [x] Guia V completada -> pendiente Guia III.
- [x] Guia V y Guia III completadas -> pendiente Guia I.
- [x] Tres guias completadas -> sin pendiente.

---

## Sprint 3 - Endpoint de envio a pendientes COMPLETADO

**Objetivo:** Crear un endpoint administrativo para enviar correos a trabajadores pendientes.

### Backend
- [x] Crear action en el ViewSet correspondiente:
  - `POST /api/aplicaciones/enviar-correos-pendientes/?ciclo_id=X`
- [x] Obtener trabajadores del ciclo seleccionado.
- [x] Identificar la guia pendiente de cada trabajador.
- [x] Buscar el `GuiaLink` activo de esa guia y ciclo.
- [x] Enviar un correo solo si:
  - El trabajador tiene correo.
  - Tiene una guia pendiente.
  - Existe link activo para esa guia.
- [x] Devolver resumen con:
  - `enviados`
  - `omitidos_sin_correo`
  - `omitidos_completos`
  - `omitidos_sin_link`
  - detalle por trabajador
- [x] Manejar errores de envio por trabajador sin detener el lote.
- [x] Agregar pruebas del endpoint con V, III, I y trabajador completo.

### Respuesta sugerida

```json
{
  "data": {
    "enviados": 10,
    "omitidos_sin_correo": 2,
    "omitidos_completos": 4,
    "omitidos_sin_link": 0,
    "detalle": [
      {
        "trabajador": "Miguel Angel",
        "correo": "miguel@example.com",
        "guia_enviada": "III",
        "estado": "enviado"
      }
    ]
  },
  "meta": {},
  "errors": []
}
```

---

## Sprint 4 - Configuracion y plantilla de correo

**Objetivo:** Preparar el envio real de correos con una plantilla clara.

### Backend
- [ ] Configurar variables de entorno SMTP:
  - `EMAIL_HOST`
  - `EMAIL_PORT`
  - `EMAIL_HOST_USER`
  - `EMAIL_HOST_PASSWORD`
  - `EMAIL_USE_TLS`
  - `DEFAULT_FROM_EMAIL`
- [ ] Crear plantilla de asunto y cuerpo del correo.
- [ ] Incluir:
  - Nombre del trabajador.
  - Guia pendiente.
  - Link directo de la guia.
  - Nombre del ciclo si esta disponible.
- [ ] Manejar errores de envio sin detener todo el lote.

### Plantilla sugerida

**Asunto:** Recordatorio NOM-035 - Guia pendiente

**Mensaje:**

Hola {{ nombre }},

Tienes pendiente completar la {{ guia }} del cuestionario NOM-035.

Puedes responderla en el siguiente enlace:
{{ link }}

Gracias.

---

## Sprint 5 - Boton en frontend

**Objetivo:** Agregar el boton para enviar recordatorios desde la pantalla de cuestionarios.

### Frontend
- [ ] Agregar boton "Enviar correos a pendientes" en `/cuestionarios`.
- [ ] Mostrar el boton solo si hay ciclo seleccionado o activo.
- [ ] Deshabilitar el boton mientras se esta enviando.
- [ ] Pedir confirmacion antes de enviar.
- [ ] Mostrar resumen al terminar:
  - Correos enviados.
  - Trabajadores sin correo.
  - Trabajadores completos.
  - Trabajadores sin link activo.
- [ ] Mostrar errores de envio de forma legible.

### UX esperada
- [ ] El admin selecciona un ciclo.
- [ ] Da clic en "Enviar correos a pendientes".
- [ ] Confirma la accion.
- [ ] El sistema muestra cuantos correos se enviaron y cuantos se omitieron.

---

## Sprint 6 - Auditoria basica de envios

**Objetivo:** Registrar evidencia de los correos enviados.

### Backend
- [ ] Crear modelo opcional `CorreoRecordatorio` o equivalente.
- [ ] Guardar:
  - Trabajador.
  - Ciclo.
  - Guia enviada.
  - Correo destino.
  - Fecha de envio.
  - Estado del envio.
  - Error si fallo.
- [ ] Agregar endpoint para consultar historial de envios si se necesita.

### Frontend
- [ ] Mostrar fecha de ultimo recordatorio enviado por trabajador si se requiere en la tabla.

---

## Sprint 7 - Pruebas finales

**Objetivo:** Validar el flujo completo.

### Pruebas manuales
- [ ] Crear trabajador con correo.
- [ ] Crear trabajador sin correo.
- [ ] Generar links de guias para un ciclo.
- [ ] Enviar recordatorios con trabajadores sin avance.
- [ ] Completar Guia V con un trabajador y reenviar: debe recibir Guia III.
- [ ] Completar Guia III con otro trabajador y reenviar: debe recibir Guia I.
- [ ] Completar las 3 guias y reenviar: no debe recibir correo.
- [ ] Confirmar que el resumen del endpoint coincide con lo enviado.

### Pruebas tecnicas
- [ ] Probar helper de guia pendiente.
- [ ] Probar endpoint con ciclo sin links.
- [ ] Probar endpoint con correos invalidos o ausentes.
- [ ] Probar fallo SMTP sin romper todo el lote.
