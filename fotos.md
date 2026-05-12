# Plan de Sprints - Foto antes de Guia III

## Objetivo general

Antes de que el trabajador conteste la Guia III, el sistema debe pedir una foto. La pantalla debe comunicarlo como un paso requerido, pero debe permitir omitirlo con un boton secundario. La foto se comprimira automaticamente para gastar el menor espacio posible en Railway y se guardara en base de datos.

---

## Sprint 1 - Backend y base de datos

**Objetivo:** Crear la estructura para registrar la foto u omision por aplicacion de Guia III.

### Backend
- [x] Crear modelo `AplicacionFoto` asociado uno a uno con `Aplicacion`.
- [x] Guardar la foto comprimida en `BinaryField` para mantenerla en base de datos.
- [x] Guardar metadatos minimos: MIME, tamanio y estado (`capturada` u `omitida`).
- [x] Crear migracion.
- [x] Registrar el modelo en admin solo como control tecnico.

---

## Sprint 2 - Compresion y API publica

**Objetivo:** Recibir la foto desde el flujo publico y reducirla antes de persistirla.

### Backend
- [x] Crear endpoint `POST /api/v1/publica/<aplicacion_token>/foto/`.
- [x] Aceptar `multipart/form-data` con `foto` u `omitida=true`.
- [x] Permitir el endpoint solo para aplicaciones de Guia III.
- [x] Comprimir con Pillow a JPEG, maximo 640 px por lado.
- [x] Usar calidad descendente para intentar quedar debajo de 80 KB.
- [x] Quitar metadatos al reescribir la imagen.
- [x] Rechazar archivos que no sean imagen o excedan 5 MB.

---

## Sprint 3 - Flujo publico en frontend

**Objetivo:** Mostrar la solicitud de foto antes de iniciar la Guia III.

### Frontend
- [x] Agregar `foto_estado` al payload publico de aplicacion.
- [x] Mostrar pantalla previa si la aplicacion es Guia III y `foto_estado` es `pendiente`.
- [x] Boton principal `Tomar foto` usando `input type="file" accept="image/*" capture="user"`.
- [x] Boton secundario `Omitir por ahora`.
- [x] Comprimir tambien en navegador con canvas antes de subir.
- [x] Continuar al cuestionario cuando la foto se capture o se omita.

---

## Sprint 4 - Panel administrativo

**Objetivo:** Que el administrador pueda ver si la foto fue tomada u omitida sin cargar imagenes pesadas.

### Frontend y API
- [x] Agregar estado `foto_guia_III` al progreso por trabajador.
- [x] Mostrar indicador en la tabla de cuestionarios:
  - Foto tomada.
  - Foto omitida.
  - Sin foto.
- [x] Evitar mostrar la imagen completa en listados.
- [x] Incluir solo el estado de foto en exportaciones CSV/Excel.

---

## Sprint 5 - Pruebas

**Objetivo:** Validar que el flujo no bloquee indebidamente el cuestionario y que la foto quede comprimida.

### Pruebas tecnicas
- [x] Subir foto valida en Guia III.
- [x] Confirmar que se convierte a JPEG y se guarda comprimida.
- [x] Omitir foto y continuar.
- [x] Rechazar foto en Guia V o Guia I.
- [x] Confirmar que la aplicacion publica devuelve `foto_estado`.

### Pruebas manuales recomendadas
- [ ] Abrir link de Guia III desde celular.
- [ ] Tomar foto y confirmar que avanza al cuestionario.
- [ ] Repetir flujo omitiendo foto.
- [ ] Verificar en `/cuestionarios` el estado de foto por trabajador.
- [ ] Revisar en Railway que el crecimiento de base de datos sea bajo.
