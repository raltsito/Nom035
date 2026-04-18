# context.md — Intra NOM-035 Platform
# Fuente de Verdad del Proyecto | Leer al inicio de cada sesion | Actualizar al cierre

---

## 1. IDENTIDAD DEL PROYECTO

| Campo                   | Valor                                                        |
|-------------------------|--------------------------------------------------------------|
| Nombre comercial        | Intra NOM-035                                                |
| Marca paraguas          | Intra (firma de servicios tecnologicos)                      |
| Tipo de producto        | SaaS B2B multitenant — gestion de cumplimiento normativo     |
| Norma implementada      | NOM-035-STPS-2018                                            |
| Idioma del sistema      | Espanol (Mexico)                                             |
| Fecha de inicio         | 2026-04-17                                                   |
| Fecha objetivo de MVP   | [PENDIENTE — definir con el cliente]                         |
| Repositorio             | https://github.com/raltsito/Nom035.git                       |
| Deploy objetivo         | Railway                                                      |

---

## 2. CONTEXTO DE NEGOCIO

### 2.1 Problema que resuelve

Las empresas mexicanas obligadas por la NOM-035 gestionan su cumplimiento
de forma manual y dispersa: hojas de calculo sin versionado, documentos en
Google Drive, formularios de Microsoft Forms, y archivos Canva sin trazabilidad.
El proceso tiene 8 fases criticas con artefactos especificos en cada una.
Cualquier error de gestion implica riesgo legal ante la STPS.

Intra NOM-035 centraliza, automatiza y hace trazable el cumplimiento completo
de la norma para cualquier empresa, gestionada por un consultor externo.

### 2.2 Roles de usuario

| Rol             | Descripcion                                                          |
|-----------------|----------------------------------------------------------------------|
| Super Admin     | Dueno del SaaS / consultor Intra. Vista global de todos los tenants. |
| Tenant Admin    | Responsable de RRHH de una empresa cliente. Vista unica de su tenant.|
| Empleado        | Solo accede para responder cuestionarios NOM-035.                    |
| Auditor/Viewer  | Acceso de solo lectura para revision de evidencias. (Post-MVP)       |

### 2.3 Modelo de negocio y tenancy

- El Super Admin (consultor) gestiona multiples empresas cliente (tenants).
- Cada tenant tiene aislamiento completo de datos (Row-Level Isolation en PostgreSQL).
- El Super Admin tiene un panel transversal con vista de todos los tenants.
- Cada tenant tiene su propio panel con sus datos aislados.
- Precio / billing: [PENDIENTE — definir estructura de cobro]

### 2.4 Restricciones legales y normativas criticas

- La norma NOM-035-STPS-2018 es de cumplimiento obligatorio en Mexico.
- Los cuestionarios (Guias I, III, V) tienen estructura FIJA por ley. No son editables.
- Segmentacion por tamano de centro de trabajo:
  - Hasta 15 trabajadores:  aplica solo Guia I.
  - 16 a 50 trabajadores:   aplica Guias I y III.
  - Mas de 50 trabajadores: aplica Guias I, III y V.
- El diagnostico y la evaluacion deben renovarse cada ano.
- Los informes de resultados son evidencia legal ante la STPS: PDF es critico.
- Firma simple es suficiente para MVP (trazabilidad de IP, usuario, timestamp).
  No se requiere e.firma SAT en esta fase.

---

## 3. ARQUITECTURA DEL SISTEMA

### 3.1 Stack tecnologico — DEFINITIVO

| Capa                    | Tecnologia                          | Razon de eleccion                               |
|-------------------------|-------------------------------------|-------------------------------------------------|
| Frontend                | React (SPA)                         | Flexibilidad, ecosistema, iteracion con IA      |
| Backend / API           | Python 3.12 + Django + DRF          | Estructura solida, ORM robusto, DRF es estandar |
| Base de datos           | PostgreSQL                          | Row-level isolation, JSON fields, madurez       |
| Autenticacion           | JWT (djangorestframework-simplejwt) | Stateless, compatible con SPA React             |
| Almacenamiento archivos | Django FileField + MEDIA_ROOT       | Local en dev, cloud-ready para Railway          |
| Generacion de PDF       | WeasyPrint (HTML/CSS to PDF)        | PDFs con estilos CSS custom. Fallback HTML+print|
| Tareas asincronas       | Celery + Redis                      | Configurado, no activo en dev local             |
| Cache                   | Redis                               | Broker de Celery + cache de API                 |
| Deploy                  | Railway                             | Stack completo soportado, CI/CD simple          |

### 3.2 Entorno de desarrollo local — DEFINITIVO

| Componente      | Version / Herramienta      | Notas                                         |
|-----------------|----------------------------|-----------------------------------------------|
| Sistema Operativo | Windows (nativo)         | No WSL — comandos nativos Windows             |
| Contenedores    | Docker Desktop             | PostgreSQL y Redis corren en contenedores     |
| Python          | 3.14.3 (real instalado)    | Entorno virtual: backend/venv/                |
| Node / NPM      | 24.x / 11.x (real)         | Para el entorno de React                      |
| Shell en Claude | bash (Unix syntax)         | Claude usa bash aunque el OS sea Windows      |

#### AVISO CRITICO: Puerto PostgreSQL
Hay una instalacion nativa de PostgreSQL en el host de Windows usando el puerto 5432.
Docker mapea el contenedor al puerto **5433** para evitar conflicto.
- Docker container: puerto interno 5432, expuesto en host como **5433**
- DATABASE_URL usa `localhost:5433`
- El .env ya tiene esta configuracion correcta.

#### AVISO: WeasyPrint en Windows
WeasyPrint no tiene dependencias nativas funcionales en Windows local.
Todos los endpoints de PDF usan el flag `WEASYPRINT_OK` (try/except al importar).
Cuando WeasyPrint NO esta disponible, el endpoint devuelve HTML con un banner
de impresion (Ctrl+P para PDF). En Railway (Linux) WeasyPrint funciona normal.

#### Migraciones — usar siempre el venv
```
cd backend
venv/Scripts/python manage.py makemigrations <app>
venv/Scripts/python manage.py migrate
```

### 3.3 Patron de arquitectura: Monolito Modular Django

Cada fase de la NOM-035 = una Django App independiente.
Apps transversales compartidas por todos los modulos.

```
Nom035/                 # Raiz del repositorio
├── backend/
│   ├── intra_nom035/       # Settings (base/dev/prod), URLs raiz, wsgi, celery
│   ├── core/               # TenantAwareModel, TenantManager, middleware, paginacion
│   ├── accounts/           # User model, JWT auth, permisos (IsSuperAdmin, IsTenantAdmin, IsTenantMember)
│   ├── tenants/            # Tenant model + CRUD + MiEmpresaView (branding)
│   ├── documents/          # Templates HTML para PDF (acta_comite, politica, difusion, acta_reunion)
│   ├── notifications/      # Notificacion model, generar endpoint
│   ├── m00_onboarding/     # Trabajador, CicloNOM
│   ├── m01_committee/      # ComiteNOM, MiembroComite, CapacitacionDC3
│   ├── m02_action_plan/    # PlanAccion, AccionMedida
│   ├── m03_policy/         # PoliticaPrevension
│   ├── m04_dissemination/  # ActividadDifusion
│   ├── m05_questionnaires/ # Cuestionario, Pregunta, Aplicacion, Respuesta
│   ├── m06_results/        # ResultadoAplicacion, ResultadoDominio
│   ├── m07_evidence/       # EvidenciaDocumento (FileField)
│   ├── m08_attendance/     # Reunion, Asistente
│   └── manage.py
├── frontend/
│   └── src/
│       ├── styles/         # variables.css, global.css, reset.css
│       ├── components/layout/  # TopNav (con campana notifs), Sidebar, MainLayout
│       ├── context/        # AuthContext
│       ├── hooks/          # useTheme
│       ├── services/       # api.js, trabajadores.js, comite.js, planAccion.js,
│       │                   # politica.js, difusion.js, evidencias.js,
│       │                   # asistencias.js, notificaciones.js, configuracion.js
│       └── pages/          # Login, Dashboard, Empresas, Trabajadores, Cuestionarios,
│                           # Responder, Resultados, Comite, PlanAccion, Politica,
│                           # Difusion, Evidencias, Asistencias, Configuracion
├── docker-compose.yml
├── .env.example
└── context.md
```

### 3.4 Multitenancy — Row-Level Isolation

- Cada modelo con datos de tenant lleva campo `tenant = ForeignKey(Tenant)`.
- `TenantAwareModel` (abstract): incluye `tenant`, `creado_en`, `actualizado_en`.
- TenantManager custom sobreescribe el queryset base para filtrar por tenant activo.
- Middleware inyecta el tenant activo en cada request desde el JWT.
- El Super Admin bypasea el filtro para ver datos de todos los tenants.
- No se usan subdominios en MVP. El ruteo es por path o por claim en el JWT.
- `IsTenantAdmin` permission: `user.rol in ('super_admin', 'tenant_admin')`.
- `IsSuperAdmin` permission: `user.rol == 'super_admin'`.
- `IsTenantMember` permission: `user.tenant is not None`.

### 3.5 Patrones estandar de implementacion

**Respuesta de API:**
```python
{ "data": ..., "meta": {}, "errors": null }
```

**ViewSet base:**
```python
class XViewSet(viewsets.ModelViewSet):
    permission_classes = (IsTenantAdmin,)
    def get_queryset(self):
        return X.objects.filter(tenant=self.request.user.tenant)
    def create(self, request, ...):
        s = XSerializer(data=request.data)
        if s.is_valid():
            obj = s.save(tenant=request.user.tenant)
            return _wrap(XSerializer(obj).data, code=201)
        return _wrap(None, errors=s.errors, code=400)
```

**PDF con WeasyPrint (fallback HTML):**
```python
html_str = render_to_string('documents/template.html', ctx)
if WEASYPRINT_OK:
    pdf = WeasyHTML(string=html_str, base_url=...).write_pdf()
    return HttpResponse(pdf, content_type='application/pdf')
else:
    return HttpResponse(html_str + _PRINT_HINT, content_type='text/html')
```

**Frontend PDF download:**
```js
const res = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
if (ct.includes('pdf')) { /* blob download */ } else { /* open in new window */ }
```

### 3.6 Decisiones de Arquitectura (ADR)

| ID     | Decision                                          | Estado   | Fecha      |
|--------|---------------------------------------------------|----------|------------|
| ADR-01 | Django sobre Flask para backend                   | CERRADA  | 2026-04-17 |
| ADR-02 | Row-level isolation sobre schema-per-tenant       | CERRADA  | 2026-04-17 |
| ADR-03 | WeasyPrint para generacion de PDF                 | CERRADA  | 2026-04-17 |
| ADR-04 | Firma simple (IP + user + timestamp) para MVP     | CERRADA  | 2026-04-17 |
| ADR-05 | Monolito modular sobre microservicios             | CERRADA  | 2026-04-17 |
| ADR-06 | Plus Jakarta Sans + Inter como sistema tipografico| CERRADA  | 2026-04-17 |
| ADR-07 | Acento #03C4CE (brand teal) sobre indigo propuesto| CERRADA  | 2026-04-17 |
| ADR-08 | Puerto Docker PG=5433 por conflicto con PG nativo | CERRADA  | 2026-04-17 |
| ADR-09 | WEASYPRINT_OK flag para fallback HTML en Windows  | CERRADA  | 2026-04-17 |
| ADR-10 | FileField local para evidencias (cloud-ready)     | CERRADA  | 2026-04-17 |
| ADR-11 | Notificaciones en-app generadas on-demand (generar endpoint) | CERRADA | 2026-04-17 |

---

## 4. SISTEMA DE DISENO

### 4.1 Branding Intra

- Logo: silhueta cerebro/cabeza humana en teal sobre fondo blanco.
- Logotipo wordmark: "INTRA" en serif bold negro + corazon rojo al final.
- Archivo: logo-intra.jpg (en raiz del proyecto local NOM035/)
- Color teal del logo: #03C4CE — este es el acento primario del sistema.
- El rojo del corazon en el logo (#E53E3E) se usa como color de peligro/error.

### 4.2 Reglas absolutas de diseno (inamovibles)

- PROHIBIDO: emojis en cualquier parte del sistema (UI, notificaciones, docs).
- PROHIBIDO: personajes ilustrativos o ilustraciones decorativas.
- PROHIBIDO: frameworks CSS externos (sin Tailwind, sin Bootstrap, sin Bulma).
- PROHIBIDO: frameworks JS pesados — solo React + Vanilla ES6+.
- OBLIGATORIO: iconos SVG monocromaticos exclusivamente de Lucide Icons.
- OBLIGATORIO: modo claro como DEFAULT. Modo oscuro opcional via boton toggle.
- OBLIGATORIO: modo oscuro = azul noche profundo (#0B1120), NO negro puro.
- OBLIGATORIO: animaciones en todas las transiciones, estados de carga y hover.
- OBLIGATORIO: glassmorphism en cards (backdrop-filter: blur).
- OBLIGATORIO: botones primarios CTA con border-radius: 9999px (pill).
- Prefijo de variables CSS: --nom-

### 4.3 Paleta de color — DEFINITIVA

```css
--nom-accent:           #03C4CE;
--nom-accent-subtle:    rgba(3, 196, 206, 0.12);
--nom-bg:               #EEF2FA;   /* claro */
--nom-bg-dark:          #0B1120;   /* oscuro */
--nom-surface:          #FFFFFF;
--nom-surface-dark:     #131D33;
--nom-danger:           #E53E3E;
--nom-danger-subtle:    rgba(229, 62, 62, 0.10);
--nom-success:          #0EA870;
--nom-success-subtle:   rgba(14, 168, 112, 0.10);
```

### 4.4 Tipografia — DEFINITIVA

- **Display / Headings:** Plus Jakarta Sans
- **Body / UI / Datos:** Inter
- Ambas via Google Fonts.

### 4.5 Layout base

- Navbar top fijo (64px): logo izq, nav links centro, acciones der (toggle tema, campana notifs, perfil).
- Sidebar icon-only (60px) a la izquierda del area de contenido, visible desktop, oculto mobile.
- Contenido principal con padding y bento grid donde aplique.
- Modales con overlay blur + animacion nomScaleIn.
- Responsive: navbar sin links en mobile, sidebar oculto.

---

## 5. MODULOS DEL SISTEMA

| ID  | Nombre del modulo          | Fase NOM-035     | Estado            | Prioridad MVP |
|-----|----------------------------|------------------|-------------------|---------------|
| M00 | Onboarding / Arranque      | Fase 0           | COMPLETADO S06    | Alta          |
| M01 | Gestion de Comite          | Fase 1           | COMPLETADO S07    | Alta          |
| M02 | Plan de Accion             | Fase 2           | COMPLETADO S07    | Alta          |
| M03 | Gestion de Politica        | Fase 3           | COMPLETADO S08    | Media         |
| M04 | Centro de Difusion         | Fase 4           | COMPLETADO S08    | Media         |
| M05 | Motor de Cuestionarios     | Fase 5 (I,III,V) | COMPLETADO S06    | CRITICO       |
| M06 | Resultados y Diagnostico   | Fase 6           | COMPLETADO S06    | CRITICO       |
| M07 | Gestion de Evidencias      | Fase 7           | COMPLETADO S09    | Media         |
| M08 | Asistencias y Minutas      | Fase 8           | COMPLETADO S09    | Media         |
| M09 | Panel Super Admin          | Transversal      | COMPLETADO S07    | Alta          |
| M10 | Multitenancy (Tenants)     | Transversal      | COMPLETADO S05    | Alta          |
| M11 | Generador de Documentos    | Transversal      | COMPLETADO S07-S09| CRITICO       |
| M12 | Autenticacion y Roles      | Transversal      | COMPLETADO S04    | CRITICO       |
| M13 | Notificaciones             | Transversal      | COMPLETADO S10    | Baja          |
| M14 | Personalizacion de Marca   | Transversal      | COMPLETADO S10    | Baja          |

### M00 — Onboarding / Arranque

**Modelos:** `Trabajador`, `CicloNOM`
- `Trabajador`: nombre, apellido, email, puesto, departamento, numero_empleado, activo, tenant
- `CicloNOM`: anio, fecha_inicio, fecha_fin, activo, tenant. `unique_together = ('tenant', 'anio')`

**Endpoints:**
- `GET/POST /api/v1/trabajadores/` — lista (busqueda por q), crear
- `GET/PATCH/DELETE /api/v1/trabajadores/{id}/`
- `POST /api/v1/trabajadores/{id}/toggle-activo/`
- `GET/POST /api/v1/ciclos/`
- `GET/PATCH/DELETE /api/v1/ciclos/{id}/`

### M01 — Gestion de Comite

**Modelos:** `ComiteNOM`, `MiembroComite`, `CapacitacionDC3`
- `ComiteNOM`: ciclo, fecha_constitucion, numero_acta, observaciones. `unique_together = ('tenant', 'ciclo')`
- `MiembroComite`: comite, nombre, puesto, tipo (presidente/secretario/vocal), email, telefono, activo
- `CapacitacionDC3`: miembro, tipo_capacitacion, fecha, horas, instructor, numero_dc3

**Endpoints:**
- `GET/POST/PATCH/DELETE /api/v1/comite/`
- `GET /api/v1/comite/{id}/acta/` — PDF: acta de constitucion con miembros y DC3
- `GET/POST/PATCH/DELETE /api/v1/miembros-comite/`
- `GET/POST/DELETE /api/v1/dc3/`

**Template PDF:** `documents/acta_comite.html`

### M02 — Plan de Accion

**Modelos:** `PlanAccion`, `AccionMedida`
- `PlanAccion`: ciclo, descripcion. `unique_together = ('tenant', 'ciclo')`
- `AccionMedida`: plan, descripcion, tipo, factor_riesgo, responsable, fecha_limite,
  prioridad, estado, avance_notas, fecha_completado
- Campo calculado `vencida`: estado not in (completado/cancelado) AND fecha_limite < hoy

**Endpoints:**
- `GET/POST /api/v1/planes-accion/`
- `GET/PATCH/DELETE /api/v1/planes-accion/{id}/`
- `GET/POST/PATCH/DELETE /api/v1/acciones/`

**Frontend:** progress bar animado + chips de estado clicables como filtros. Filas rojas cuando `vencida=True`.

### M03 — Gestion de Politica

**Modelo:** `PoliticaPrevension`
- ciclo, titulo, contenido (texto libre con plantilla NOM-035 pre-rellena),
  estado (borrador/vigente/archivada), firmante_nombre, firmante_puesto, fecha_aprobacion
- `unique_together = ('tenant', 'ciclo')`

**Endpoints:**
- `GET/POST/PATCH/DELETE /api/v1/politica/`
- `POST /api/v1/politica/{id}/aprobar/` — estado → vigente, fecha_aprobacion = hoy
- `GET /api/v1/politica/{id}/pdf/` — PDF de la politica firmada

**Template PDF:** `documents/politica_prevension.html`

**Frontend:** Tab toggle Contenido / Vista previa. Vista previa renderiza doc con firma.

### M04 — Centro de Difusion

**Modelo:** `ActividadDifusion`
- ciclo, tipo (platica/correo/cartel/reunion/intranet/otro), titulo, descripcion,
  fecha, num_participantes, responsable

**Endpoints:**
- `GET/POST/PATCH/DELETE /api/v1/actividades-difusion/` — filtros: ciclo_id, tipo
- `GET /api/v1/actividades-difusion/reporte/?ciclo_id=X` — PDF reporte de actividades

**Meta en list:** `{ count, total_participantes, por_tipo: { tipo: count } }`

**Template PDF:** `documents/difusion.html`

### M05 — Motor de Cuestionarios (CRITICO)

**Modelos:** Cuestionario, Pregunta, Aplicacion, Respuesta (app: `m05_questionnaires`)
- Cuestionarios fijos NOM-035: Guia I, Guia III, Guia V
- Aplicacion por trabajador con token unico para link de respuesta
- Pagina publica `/responder/:token` (sin autenticacion requerida)
- Estados de aplicacion: pendiente / en_proceso / completado

### M06 — Resultados y Diagnostico (CRITICO)

**Modelos:** ResultadoAplicacion, ResultadoDominio (app: `m06_results`)
- Categorias de riesgo: nulo / bajo / medio / alto / muy_alto
- Dashboard de resultados con distribucion de riesgo
- Informes generados por ciclo

### M07 — Gestion de Evidencias

**Modelo:** `EvidenciaDocumento`
- ciclo, modulo (comite/plan/politica/difusion/aplicacion/otro), nombre, descripcion,
  archivo (FileField `evidencias/%Y/%m/`), tamanio (bytes), tipo_mime, subido_por (FK User)

**Endpoints:**
- `GET /api/v1/evidencias/` — filtros: ciclo_id, modulo. Meta: count, total_bytes, por_modulo
- `POST /api/v1/evidencias/` — multipart/form-data. Auto-rellena tamanio y tipo_mime
- `DELETE /api/v1/evidencias/{id}/` — elimina registro Y archivo fisico
- `GET /api/v1/evidencias/{id}/download/` — stream autenticado

**Frontend:** drag & drop zone, progress bar real con XHR, grid de cards con icono por MIME,
chips filtrables por modulo, descarga autenticada.

### M08 — Asistencias y Minutas

**Modelos:** `Reunion`, `Asistente`
- `Reunion`: ciclo, tipo (comite/capacitacion/seguimiento/informativa/otra),
  titulo, fecha, lugar, agenda, minuta
- `Asistente`: reunion (FK), nombre, puesto, firma_recibida (bool)

**Endpoints:**
- `GET/POST/PATCH/DELETE /api/v1/reuniones/` — filtros: ciclo_id, tipo. Meta: count, por_tipo
- `GET /api/v1/reuniones/{id}/acta/` — PDF acta con lista de asistencia + minuta
- `GET/POST/PATCH/DELETE /api/v1/asistentes/`

**Template PDF:** `documents/acta_reunion.html`

**Frontend:** accordion por reunion, toggle de firma por asistente (PATCH firma_recibida),
modal de asistente inline, descarga de acta individual.

### M09 — Panel Super Admin

**Implementado en:** `tenants/views.py` como actions extra del `TenantViewSet`

- `GET /api/v1/tenants/{id}/stats/` — KPIs: trabajadores, ciclos, aplicaciones, completadas,
  resultados, distribucion de riesgo (bajo/medio/alto/muy_alto)
- `GET/POST /api/v1/tenants/{id}/usuarios/` — lista y crea usuarios del tenant (tenant_admin)
- **Frontend:** drawer lateral en `/empresas` con tabs Estadisticas | Usuarios

### M11 — Generador de Documentos

**Templates HTML en** `documents/templates/documents/`:
- `acta_comite.html` — acta de constitucion de comite con miembros y DC3
- `politica_prevension.html` — politica firmada con header, cuerpo y bloque de firma
- `difusion.html` — reporte de actividades de difusion con tabla y KPIs
- `acta_reunion.html` — acta de reunion con agenda, minuta y lista de asistencia

Todos usan el patron WeasyPrint + fallback HTML con banner de impresion.

### M13 — Notificaciones

**Modelo:** `Notificacion` (en app `notifications`, NO extiende TenantAwareModel)
- usuario (FK User), tipo, titulo, mensaje, leida (bool), url_destino, referencia
- `unique_together = ('usuario', 'tipo', 'referencia')` — evita duplicados en generar

**Tipos:** accion_vencida | accion_por_vencer | ciclo_por_cerrar | info

**Endpoints:**
- `GET /api/v1/notificaciones/` — lista ultimas 50, meta: no_leidas
- `PATCH /api/v1/notificaciones/{id}/` — marca como leida
- `DELETE /api/v1/notificaciones/{id}/`
- `POST /api/v1/notificaciones/marcar_leidas/` — marca todas
- `POST /api/v1/notificaciones/generar/` — genera notifs para acciones vencidas,
  por vencer en 7 dias y ciclos por cerrar en 30 dias. Devuelve lista actualizada.

**Frontend:** campana en TopNav con badge rojo de no leidas. Al cargar el nav se llama
`generar`. Dropdown con ultimas 8, icono por tipo, click navega + marca leida.

### M14 — Personalizacion de Marca

**Campos agregados al modelo `Tenant`:**
- `logo_url` (URLField blank), `sitio_web` (URLField blank),
  `telefono_contacto` (CharField blank), `direccion` (CharField blank)

**Endpoints:**
- `GET /api/v1/tenants/mi-empresa/` — devuelve datos de la empresa del usuario autenticado
- `PATCH /api/v1/tenants/mi-empresa/` — actualiza campos de branding (IsTenantAdmin)

**Frontend:** `/configuracion` — layout dos columnas: tarjeta de vista previa + formulario
con 3 secciones (datos generales, marca e identidad, contacto). Preview de logo en tiempo real.
Accesible desde el dropdown del usuario en TopNav ("Configuracion de empresa").

---

## 6. FLUJO DE IMPLEMENTACION POR EMPRESA (TENANT)

```
[Onboarding]         Empresa se registra, configura datos basicos, define
    |                numero de trabajadores (determina guias aplicables).
    v
[Comite]             Se conforma el comite NOM-035, se registran miembros,
    |                se capturan capacitaciones (DC3), se genera acta PDF.
    v
[Plan de Accion]     Se registran acciones correctivas/preventivas con
    |                responsable, fecha limite, prioridad y estado.
    v
[Politica]           Se genera y aprueba la politica de prevencion con
    |                plantilla NOM-035 pre-rellena. PDF firmado.
    v
[Difusion]           Se registran actividades de difusion a trabajadores
    |                (platicas, correos, carteles, reuniones).
    v
[Cuestionarios]      Se aplican las guias I, III y/o V a la muestra
    |                representativa via link unico por trabajador.
    v
[Resultados]         Se procesan respuestas, se genera informe diagnostico
    |                en PDF con distribucion de riesgo por categoria.
    v
[Evidencias]         Se consolida toda la evidencia del ciclo: archivos
    |                PDF/Word/Excel/imagen subidos al repositorio documental.
    v
[Asistencias]        Se registran reuniones del ciclo con agenda, minuta
    |                y lista de asistencia firmada (PDF).
    v
[Cierre de ciclo]    El sistema genera notificaciones automaticas cuando
                     se acerca la fecha de cierre del ciclo.
```

---

## 7. ESQUEMA DE BASE DE DATOS

```
Tenant
  ├── nombre, rfc, giro, num_trabajadores
  ├── activo, consultor → FK User (super_admin)
  └── logo_url, sitio_web, telefono_contacto, direccion  [M14]

User (AbstractUser)
  ├── email, first_name, last_name
  ├── rol: super_admin | tenant_admin | empleado | auditor
  └── tenant → FK Tenant (null para super_admin)

Trabajador (TenantAwareModel)          [M00]
  └── nombre, apellido, email, puesto, departamento, numero_empleado, activo

CicloNOM (TenantAwareModel)            [M00]
  └── anio, fecha_inicio, fecha_fin, activo. unique(tenant, anio)

ComiteNOM (TenantAwareModel)           [M01]
  └── ciclo, fecha_constitucion, numero_acta, observaciones. unique(tenant, ciclo)

MiembroComite (TenantAwareModel)       [M01]
  └── comite, nombre, puesto, tipo, email, telefono, activo

CapacitacionDC3 (TenantAwareModel)     [M01]
  └── miembro, tipo_capacitacion, fecha, horas, instructor, numero_dc3

PlanAccion (TenantAwareModel)          [M02]
  └── ciclo, descripcion. unique(tenant, ciclo)

AccionMedida (TenantAwareModel)        [M02]
  └── plan, descripcion, tipo, factor_riesgo, responsable,
      fecha_limite, prioridad, estado, avance_notas, fecha_completado
  [computed] vencida: estado activo AND fecha_limite < hoy

PoliticaPrevension (TenantAwareModel)  [M03]
  └── ciclo, titulo, contenido, estado, firmante_nombre,
      firmante_puesto, fecha_aprobacion. unique(tenant, ciclo)

ActividadDifusion (TenantAwareModel)   [M04]
  └── ciclo, tipo, titulo, descripcion, fecha, num_participantes, responsable

[M05/M06: Cuestionario, Pregunta, Aplicacion, Respuesta, ResultadoAplicacion, ResultadoDominio]

EvidenciaDocumento (TenantAwareModel)  [M07]
  └── ciclo, modulo, nombre, descripcion, archivo (FileField),
      tamanio, tipo_mime, subido_por → FK User

Reunion (TenantAwareModel)             [M08]
  └── ciclo, tipo, titulo, fecha, lugar, agenda, minuta

Asistente (TenantAwareModel)           [M08]
  └── reunion, nombre, puesto, firma_recibida

Notificacion                           [M13]
  └── usuario → FK User, tipo, titulo, mensaje, leida,
      url_destino, referencia. unique(usuario, tipo, referencia)
```

---

## 8. CONTRATOS DE API

Prefijo: `/api/v1/`
Autenticacion: `Authorization: Bearer <access_token>`
Respuesta estandar: `{ data, meta, errors }`

### Auth
```
POST /api/v1/auth/login/          { email, password } → { access, refresh, user }
POST /api/v1/auth/logout/
POST /api/v1/auth/token/refresh/
GET  /api/v1/accounts/me/         → { id, email, first_name, last_name, rol, tenant }
```

### Tenants (Super Admin)
```
GET/POST        /api/v1/tenants/
GET/PATCH/DEL   /api/v1/tenants/{id}/
POST            /api/v1/tenants/{id}/toggle-activo/
GET             /api/v1/tenants/{id}/stats/
GET/POST        /api/v1/tenants/{id}/usuarios/
GET/PATCH       /api/v1/tenants/mi-empresa/   (Tenant Admin)
```

### Onboarding
```
GET/POST/PATCH/DEL  /api/v1/trabajadores/   ?q=
POST                /api/v1/trabajadores/{id}/toggle-activo/
GET/POST/PATCH/DEL  /api/v1/ciclos/
```

### Comite
```
GET/POST/PATCH/DEL  /api/v1/comite/          ?ciclo_id=
GET                 /api/v1/comite/{id}/acta/
GET/POST/PATCH/DEL  /api/v1/miembros-comite/
GET/POST/DEL        /api/v1/dc3/
```

### Plan de Accion
```
GET/POST/PATCH/DEL  /api/v1/planes-accion/   ?ciclo_id=
GET/POST/PATCH/DEL  /api/v1/acciones/        ?plan_id= &estado= &prioridad=
```

### Politica
```
GET/POST/PATCH/DEL  /api/v1/politica/        ?ciclo_id=
POST                /api/v1/politica/{id}/aprobar/
GET                 /api/v1/politica/{id}/pdf/
```

### Difusion
```
GET/POST/PATCH/DEL  /api/v1/actividades-difusion/  ?ciclo_id= &tipo=
GET                 /api/v1/actividades-difusion/reporte/?ciclo_id=
```

### Evidencias
```
GET/POST            /api/v1/evidencias/       ?ciclo_id= &modulo=   (multipart)
DEL                 /api/v1/evidencias/{id}/
GET                 /api/v1/evidencias/{id}/download/
```

### Asistencias
```
GET/POST/PATCH/DEL  /api/v1/reuniones/        ?ciclo_id= &tipo=
GET                 /api/v1/reuniones/{id}/acta/
GET/POST/PATCH/DEL  /api/v1/asistentes/
```

### Notificaciones
```
GET                 /api/v1/notificaciones/
PATCH               /api/v1/notificaciones/{id}/   (marca leida)
DEL                 /api/v1/notificaciones/{id}/
POST                /api/v1/notificaciones/marcar_leidas/
POST                /api/v1/notificaciones/generar/
```

---

## 9. EXPORTABLES

| Formato | Prioridad | Uso                                               |
|---------|-----------|---------------------------------------------------|
| PDF     | CRITICO   | Informes, actas, politicas, evidencias para STPS  |
| Excel   | Deseable  | Base de datos de trabajadores, respuestas raw     |

PDFs implementados: acta de comite, politica de prevencion, reporte de difusion, acta de reunion.
Pendiente: informe diagnostico de resultados (M06), justificacion de muestra (M05).

---

## 10. PREGUNTAS ABIERTAS

| ID  | Pregunta                                                            | Estado      |
|-----|---------------------------------------------------------------------|-------------|
| Q01 | Nombre comercial del producto                                       | CERRADA     |
| Q02 | Paleta de color e identidad visual                                  | CERRADA     |
| Q03 | Modelo de negocio y estructura de precios / billing                 | PENDIENTE   |
| Q04 | Stack tecnologico                                                   | CERRADA     |
| Q05 | Estrategia de multitenancy                                          | CERRADA     |
| Q06 | Integraciones externas (correo transaccional, etc.)                 | PENDIENTE   |
| Q07 | Exportables criticos                                                | CERRADA     |
| Q08 | Firma electronica                                                   | CERRADA     |
| Q09 | Modelo de uso (consultores vs. directo)                             | CERRADA     |
| Q10 | Branding / logo de Intra                                            | CERRADA     |
| Q11 | Entorno de desarrollo local                                         | CERRADA     |
| Q12 | Repositorio de codigo                                               | CERRADA     |
| Q13 | Almacenamiento de archivos en produccion (S3 vs Railway volumes)    | PENDIENTE   |

---

## 11. ARTEFACTOS DE REFERENCIA

| Artefacto                              | Tipo        | Ubicacion / URL                                          |
|----------------------------------------|-------------|----------------------------------------------------------|
| README requerimientos NOM-035          | GitHub      | https://github.com/IngRaulAlvarado/CheckList-NOM-035     |
| Informe diagnostico LEAR Tlahuac       | PDF local   | NOM035/INFORME DIAGNOSTICO NOM035 LEAR TLAHUAC.pdf       |
| Logo Intra                             | JPG local   | NOM035/logo-intra.jpg                                    |
| Video de referencia 1                  | YouTube     | https://www.youtube.com/watch?v=WgxQ2YRFo8s              |
| Video de referencia 2                  | YouTube     | https://www.youtube.com/watch?v=WppMCBHRFAI              |
| Cuestionarios NOM-035 (I, III, V)      | Google Sheet| https://docs.google.com/spreadsheets/d/1a4-Imh3Rxs...   |

---

## 12. REGISTRO DE SESIONES

| Sesion | Fecha      | Resumen                                                                                                     | Proximos pasos                        |
|--------|------------|-------------------------------------------------------------------------------------------------------------|---------------------------------------|
| S01    | 2026-04-17 | Definicion de reglas, stack, diseno, multitenancy, roles                                                    | Responder Q10-Q12                     |
| S02    | 2026-04-17 | Cierre de Q10-Q12: logo, env local, repo, paleta y typo final                                               | Scaffolding del proyecto              |
| S03    | 2026-04-17 | Scaffolding completo: Django + React + Docker. 0 errores.                                                   | Levantar Docker, migrar, M12 auth     |
| S04    | 2026-04-17 | Docker up (PG 5433, Redis 6379), migraciones aplicadas, M12 completo. Super Admin creado.                  | M10 Multitenancy + M00 Onboarding     |
| S05    | 2026-04-17 | Rediseno front completo (navbar top + sidebar icon + glass + modo claro default). M10 completo.             | M00 Onboarding → M05 Cuestionarios    |
| S06    | 2026-04-17 | Login integrado (split card + carousel). Logo real. M00 completo: Trabajador + CicloNOM. M05+M06 completados. | M09 Panel SA + M01 Comite            |
| S07    | 2026-04-17 | M09 (drawer Empresas con stats+usuarios), M01 Comite (ComiteNOM+Miembros+DC3+PDF acta), M02 Plan de Accion. | M03 Politica → M04 Difusion           |
| S08    | 2026-04-17 | M03 Politica (plantilla NOM-035, aprobar, PDF), M04 Difusion (actividades, reporte PDF).                    | M07 Evidencias → M08 Asistencias      |
| S09    | 2026-04-17 | M07 Evidencias (FileField, multipart upload con progress, download autenticado), M08 Asistencias (Reunion+Asistente, firma toggle, PDF acta). | M13 Notificaciones + M14 Marca |
| S10    | 2026-04-17 | M13 Notificaciones (campana TopNav, badge, dropdown, generar endpoint), M14 Marca (branding Tenant, mi-empresa endpoint, /configuracion page). | Deploy a Railway / pruebas integracion |

---

## 13. ESTADO ACTUAL — RESUMEN EJECUTIVO (S10)

**Backend completado:**
- 11 apps Django con modelos, serializers, views y urls
- 14+ endpoints PDF (WeasyPrint + fallback HTML)
- Sistema de notificaciones in-app generadas on-demand
- Branding por tenant (logo, sitio, telefono, direccion)
- Migraciones aplicadas y DB sincronizada

**Frontend completado:**
- 14 paginas React con CSS Modules
- TopNav con campana de notificaciones (badge + dropdown)
- Sidebar icon-only con tooltips para todos los modulos
- Sistema de tema claro/oscuro (localStorage nom-theme)
- Descarga de PDFs autenticada con Bearer token
- Upload de archivos con drag & drop y progress bar real

**Pendiente para produccion:**
- Configurar almacenamiento de archivos en Railway (FileField → S3/Cloud)
- Activar WeasyPrint en entorno Linux Railway
- Pruebas de integracion completas
- Deploy CI/CD en Railway
- Definir modelo de billing (Q03)
- Correo transaccional (Q06)

---

## 14. GLOSARIO

| Termino             | Definicion                                                        |
|---------------------|-------------------------------------------------------------------|
| NOM-035             | Norma Oficial Mexicana de riesgos psicosociales en el trabajo     |
| STPS                | Secretaria del Trabajo y Prevision Social                         |
| Centro de trabajo   | Unidad operativa de una empresa sujeta a la norma                 |
| Guia I              | Cuestionario basico (todos los centros de trabajo)                |
| Guia III            | Cuestionario para centros de 16+ trabajadores                     |
| Guia V              | Cuestionario para centros de 50+ trabajadores                     |
| OIL                 | Identificacion y analisis de riesgos organizacionales             |
| DC3                 | Constancia de habilidades laborales (certificado de capacitacion) |
| Tenant              | Empresa cliente dentro del SaaS                                   |
| Super Admin         | Consultor Intra — administra todos los tenants                    |
| Tenant Admin        | Administrador de una empresa cliente                              |
| Row-Level Isolation | Aislamiento de datos por campo tenant_id en cada tabla            |
| TenantAwareModel    | Clase base abstracta Django con tenant + creado_en + actualizado_en|
| WeasyPrint          | Libreria Python para generar PDFs desde HTML/CSS                  |
| WEASYPRINT_OK       | Flag booleano para fallback HTML cuando WeasyPrint no esta listo  |
| DRF                 | Django REST Framework                                             |
| Plus Jakarta Sans   | Fuente display del sistema (headings, KPIs)                       |
| Inter               | Fuente de cuerpo del sistema (forms, tablas, texto)               |
