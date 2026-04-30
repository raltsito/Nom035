"""
Crea un tenant demo grande y reusable para mostrar el sistema con datos vivos.

Notas:
- Los nombres, correos, telefonos y empresa son sinteticos y solo para demo.
- El comando es idempotente: puede correrse varias veces sin duplicar registros clave.

Uso:
    python manage.py seed_demo_tenant_masivo
"""
from __future__ import annotations

import random
import re
from datetime import date, timedelta

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import User
from m00_onboarding.models import CicloNOM, Trabajador
from m01_committee.models import CapacitacionDC3, ComiteNOM, MiembroComite
from m02_action_plan.models import AccionMedida, PlanAccion
from m03_policy.models import PoliticaPrevension
from m04_dissemination.models import ActividadDifusion
from m05_questionnaires.models import Aplicacion, Cuestionario, RespuestaPregunta
from m06_results.models import ResultadoAplicacion, ResultadoDominio
from m06_results.scoring import calcular_resultado
from m07_evidence.models import EvidenciaDocumento
from m08_attendance.models import Asistente, Reunion
from tenants.models import Tenant


SEED = 2035

TENANT_DATA = {
    "nombre": "Grupo Horizonte Industrial Demo, S.A. de C.V.",
    "rfc": "GHD260120AB1",
    "giro": "Manufactura avanzada, logistica y servicios operativos",
    "num_trabajadores": 180,
    "telefono_contacto": "55 5010 0100",
    "sitio_web": "https://demo-horizonte-industrial.mx",
    "direccion": "Av. Industria 1200, Parque Tecnologico Norte, Monterrey, Nuevo Leon, C.P. 66480",
}

ADMIN_USER = {
    "email": "admin.demo@horizonte-industrial.mx",
    "username": "horizonte_demo_admin",
    "first_name": "Daniel",
    "last_name": "Ortega Salas",
    "password": "DemoTenant2035!",
    "rol": User.TENANT_ADMIN,
}

EXTRA_USERS = [
    {
        "email": "rh.demo@horizonte-industrial.mx",
        "first_name": "Lucia",
        "last_name": "Mora Campos",
        "password": "DemoTenant2035!",
        "rol": User.TENANT_ADMIN,
    },
    {
        "email": "auditoria.demo@horizonte-industrial.mx",
        "first_name": "Pablo",
        "last_name": "Rios Beltran",
        "password": "DemoTenant2035!",
        "rol": User.AUDITOR,
    },
    {
        "email": "supervision.turnoa@horizonte-industrial.mx",
        "first_name": "Erika",
        "last_name": "Solis Fuentes",
        "password": "DemoTenant2035!",
        "rol": User.EMPLEADO,
    },
    {
        "email": "supervision.turnob@horizonte-industrial.mx",
        "first_name": "Martin",
        "last_name": "Cruz Padilla",
        "password": "DemoTenant2035!",
        "rol": User.EMPLEADO,
    },
]

NOMBRES_M = [
    "Daniel", "Luis", "Jorge", "Carlos", "Miguel", "Ramon", "Adrian", "Victor",
    "Omar", "Pablo", "Ricardo", "Hector", "Emilio", "Ivan", "Arturo", "Ruben",
    "Sergio", "Mario", "Rafael", "Edgar",
]
NOMBRES_F = [
    "Lucia", "Mariana", "Sandra", "Patricia", "Erika", "Claudia", "Paola", "Diana",
    "Gabriela", "Lorena", "Monica", "Daniela", "Yadira", "Alicia", "Miriam", "Silvia",
    "Andrea", "Vanessa", "Jessica", "Berenice",
]
APELLIDOS_1 = [
    "Garcia", "Lopez", "Martinez", "Hernandez", "Gonzalez", "Perez", "Sanchez", "Ramirez",
    "Torres", "Flores", "Rivera", "Gomez", "Diaz", "Vazquez", "Castillo", "Mendoza",
    "Ruiz", "Aguilar", "Morales", "Ortiz",
]
APELLIDOS_2 = [
    "Navarro", "Salas", "Campos", "Fuentes", "Delgado", "Benitez", "Cortes", "Rios",
    "Pineda", "Valdez", "Beltran", "Mejia", "Padilla", "Rosales", "Villarreal", "Zamora",
    "Escobar", "Meza", "Bravo", "Cuevas",
]

AREA_CONFIG = [
    {"area": "Direccion", "puestos": ["Director General", "Directora Administrativa"], "size": 2},
    {"area": "Recursos Humanos", "puestos": ["Coordinador de RH", "Generalista de RH", "Analista de Desarrollo Organizacional"], "size": 10},
    {"area": "Seguridad e Higiene", "puestos": ["Jefe de Seguridad", "Tecnico de Seguridad Industrial"], "size": 8},
    {"area": "Produccion", "puestos": ["Supervisor de Produccion", "Tecnico de Linea", "Operador de Ensamble"], "size": 64},
    {"area": "Calidad", "puestos": ["Ingeniero de Calidad", "Inspector de Calidad", "Analista de Calidad"], "size": 18},
    {"area": "Mantenimiento", "puestos": ["Supervisor de Mantenimiento", "Tecnico Electromecanico", "Tecnico de Mantenimiento"], "size": 18},
    {"area": "Logistica", "puestos": ["Coordinador de Logistica", "Planeador de Materiales", "Auxiliar de Almacen"], "size": 20},
    {"area": "Compras", "puestos": ["Comprador", "Analista de Abastecimiento"], "size": 8},
    {"area": "Finanzas", "puestos": ["Analista Financiero", "Auxiliar Contable"], "size": 8},
    {"area": "Sistemas", "puestos": ["Administrador de Sistemas", "Soporte TI", "Analista BI"], "size": 10},
    {"area": "Comercial", "puestos": ["Ejecutivo Comercial", "Coordinador de Cuenta"], "size": 8},
    {"area": "Servicio Medico", "puestos": ["Medico Laboral", "Enfermera Industrial"], "size": 6},
]

CYCLES = [
    {
        "anio": 2024,
        "estado": "cerrado",
        "fecha_inicio": date(2024, 1, 8),
        "fecha_cierre": date(2024, 12, 12),
        "notas": "Ciclo demo 2024 cerrado con seguimiento documental completo.",
        "apps": {"completadas": 150, "en_progreso": 15},
    },
    {
        "anio": 2025,
        "estado": "completado",
        "fecha_inicio": date(2025, 1, 13),
        "fecha_cierre": date(2025, 11, 28),
        "notas": "Ciclo demo 2025 con resultados y plan de accion ejecutado en su mayoria.",
        "apps": {"completadas": 168, "en_progreso": 6},
    },
    {
        "anio": 2026,
        "estado": "en_progreso",
        "fecha_inicio": date(2026, 1, 12),
        "fecha_cierre": None,
        "notas": "Ciclo activo 2026 con aplicaciones pendientes y evidencia de seguimiento.",
        "apps": {"completadas": 112, "en_progreso": 28},
    },
]

POLICY_TEMPLATE = (
    "En {empresa} promovemos un entorno organizacional favorable y el respeto "
    "a la dignidad de las personas trabajadoras. La empresa se compromete a "
    "identificar, prevenir y atender factores de riesgo psicosocial, asi como "
    "actos de violencia laboral, conforme a la NOM-035-STPS-2018.\n\n"
    "Compromisos permanentes:\n"
    "1. Mantener cargas de trabajo razonables y canales de comunicacion claros.\n"
    "2. Atender reportes por medio de RH y del Comite NOM-035.\n"
    "3. Difundir acciones preventivas, capacitaciones y resultados generales.\n"
    "4. Revisar la politica al inicio de cada ciclo y cuando existan cambios relevantes.\n"
)


def slugify_text(value: str) -> str:
    base = re.sub(r"[^a-z0-9]+", ".", value.lower()).strip(".")
    return re.sub(r"\.+", ".", base)


def worker_display_name(trabajador: Trabajador) -> str:
    return f"{trabajador.nombre} {trabajador.apellido_paterno} {trabajador.apellido_materno}".strip()


class Command(BaseCommand):
    help = "Crea un tenant demo grande con multiples modulos, ciclos y muchos trabajadores"

    def handle(self, *args, **options):
        random.seed(SEED)

        with transaction.atomic():
            super_admin = self._ensure_super_admin()
            tenant = self._create_tenant(super_admin)
            users = self._create_users(tenant)
            workers = self._create_workers(tenant)
            cuestionario = self._get_questionnaire()
            ciclos = self._create_cycles(tenant)

            for index, ciclo in enumerate(ciclos):
                self._create_committee(tenant, ciclo, workers, index)
                self._create_policy(tenant, ciclo, users["admin"])
                self._create_dissemination(tenant, ciclo, workers, index)
                self._create_action_plan(tenant, ciclo, workers, index)
                self._create_meetings(tenant, ciclo, workers, index)
                self._create_evidence(tenant, ciclo, users["admin"], index)
                if cuestionario:
                    self._create_applications(tenant, ciclo, workers, cuestionario)

        self._print_summary()

    def _ensure_super_admin(self) -> User:
        user, created = User.objects.get_or_create(
            email="superadmin@intra.com",
            defaults={
                "username": "superadmin",
                "first_name": "Super",
                "last_name": "Admin",
                "rol": User.SUPER_ADMIN,
                "is_active": True,
                "is_staff": True,
            },
        )
        if created:
            user.set_password("Admin123!")
            user.save()
            self._ok("Super admin creado")
        else:
            self._skip("Super admin ya existe")
        return user

    def _create_tenant(self, super_admin: User) -> Tenant:
        tenant, created = Tenant.objects.get_or_create(
            rfc=TENANT_DATA["rfc"],
            defaults={**TENANT_DATA, "consultor": super_admin},
        )
        if created:
            self._ok(f'Tenant "{tenant.nombre}" creado')
        else:
            changed = False
            for field in ("nombre", "giro", "num_trabajadores", "telefono_contacto", "sitio_web", "direccion"):
                value = TENANT_DATA[field]
                if getattr(tenant, field) != value:
                    setattr(tenant, field, value)
                    changed = True
            if tenant.consultor_id != super_admin.id:
                tenant.consultor = super_admin
                changed = True
            if changed:
                tenant.save()
                self._ok(f'Tenant "{tenant.nombre}" actualizado')
            else:
                self._skip(f'Tenant "{tenant.nombre}" ya existe')
        return tenant

    def _create_users(self, tenant: Tenant) -> dict[str, User]:
        users: dict[str, User] = {}
        users["admin"] = self._upsert_user({**ADMIN_USER, "tenant": tenant})
        for extra in EXTRA_USERS:
            user = self._upsert_user({**extra, "tenant": tenant})
            users[user.email] = user
        self._ok(f"{1 + len(EXTRA_USERS)} usuarios del tenant listos")
        return users

    def _upsert_user(self, data: dict) -> User:
        defaults = {
            "username": data.get("username", data["email"]),
            "first_name": data["first_name"],
            "last_name": data["last_name"],
            "rol": data["rol"],
            "tenant": data["tenant"],
            "is_active": True,
        }
        user, created = User.objects.get_or_create(email=data["email"], defaults=defaults)
        if created:
            user.set_password(data["password"])
            user.save()
            self._ok(f"  Usuario: {data['email']}")
            return user

        changed = False
        for field, value in defaults.items():
            if getattr(user, field) != value:
                setattr(user, field, value)
                changed = True
        if changed:
            user.save()
        return user

    def _create_workers(self, tenant: Tenant) -> list[Trabajador]:
        workers: list[Trabajador] = []
        area_slots: list[dict] = []
        for config in AREA_CONFIG:
            area_slots.extend([config] * config["size"])

        for index, config in enumerate(area_slots, start=1):
            worker_data = self._build_worker_data(index, config)
            worker, created = Trabajador.all_objects.get_or_create(
                tenant=tenant,
                num_empleado=worker_data["num_empleado"],
                defaults={**worker_data, "tenant": tenant},
            )
            if not created:
                changed = False
                for field, value in worker_data.items():
                    if getattr(worker, field) != value:
                        setattr(worker, field, value)
                        changed = True
                if changed:
                    worker.save()
            workers.append(worker)

        self._ok(f"{len(workers)} trabajadores listos para demo")
        return workers

    def _build_worker_data(self, index: int, config: dict) -> dict:
        is_female = index % 2 == 0
        first_names = NOMBRES_F if is_female else NOMBRES_M
        nombre = first_names[(index * 3) % len(first_names)]
        apellido_paterno = APELLIDOS_1[(index * 5) % len(APELLIDOS_1)]
        apellido_materno = APELLIDOS_2[(index * 7) % len(APELLIDOS_2)]
        puesto = config["puestos"][(index // 2) % len(config["puestos"])]
        tipo = "planta"
        if index % 13 == 0:
            tipo = "eventual"
        elif index % 17 == 0:
            tipo = "subcontratado"

        correo_base = slugify_text(f"{nombre}.{apellido_paterno}.{index}")
        return {
            "nombre": nombre,
            "apellido_paterno": apellido_paterno,
            "apellido_materno": apellido_materno,
            "num_empleado": f"GHD-{index:03d}",
            "email": f"{correo_base}@horizonte-industrial.mx",
            "puesto": puesto,
            "area": config["area"],
            "tipo_contratacion": tipo,
            "activo": True,
        }

    def _get_questionnaire(self) -> Cuestionario | None:
        cuestionario = Cuestionario.objects.filter(clave="V").first()
        if cuestionario:
            self._ok("Cuestionario Guia V listo")
        else:
            self.stdout.write(
                self.style.WARNING(
                    "No existe la Guia V. Ejecuta primero: python manage.py seed_cuestionarios"
                )
            )
        return cuestionario

    def _create_cycles(self, tenant: Tenant) -> list[CicloNOM]:
        cycles = []
        for data in CYCLES:
            ciclo, created = CicloNOM.all_objects.get_or_create(
                tenant=tenant,
                anio=data["anio"],
                defaults={
                    "tenant": tenant,
                    "estado": data["estado"],
                    "fecha_inicio": data["fecha_inicio"],
                    "fecha_cierre": data["fecha_cierre"],
                    "notas": data["notas"],
                },
            )
            if not created:
                changed = False
                for field in ("estado", "fecha_inicio", "fecha_cierre", "notas"):
                    if getattr(ciclo, field) != data[field]:
                        setattr(ciclo, field, data[field])
                        changed = True
                if changed:
                    ciclo.save()
            cycles.append(ciclo)
        self._ok(f"{len(cycles)} ciclos NOM listos")
        return cycles

    def _create_committee(self, tenant: Tenant, ciclo: CicloNOM, workers: list[Trabajador], offset: int) -> None:
        comite, created = ComiteNOM.all_objects.get_or_create(
            tenant=tenant,
            ciclo=ciclo,
            defaults={
                "tenant": tenant,
                "fecha_constitucion": ciclo.fecha_inicio + timedelta(days=10),
                "numero_acta": f"ACTA-{ciclo.anio}-001",
                "observaciones": (
                    "Comite de seguimiento NOM-035 integrado para atender acciones preventivas, "
                    "seguimiento de cuestionarios y revision del plan anual."
                ),
            },
        )
        if created:
            self._ok(f"Comite {ciclo.anio} creado")

        selected = [
            ("presidente", workers[0]),
            ("secretario", workers[9]),
            ("vocal", workers[24 + offset]),
        ]
        for idx, (tipo, worker) in enumerate(selected):
            miembro, was_created = MiembroComite.all_objects.get_or_create(
                tenant=tenant,
                comite=comite,
                nombre=worker_display_name(worker),
                defaults={
                    "tenant": tenant,
                    "puesto": worker.puesto,
                    "tipo": tipo,
                    "email": worker.email,
                    "telefono": f"55 5010 01{offset}{idx}",
                    "activo": True,
                },
            )
            if not was_created:
                changed = False
                payload = {
                    "puesto": worker.puesto,
                    "tipo": tipo,
                    "email": worker.email,
                    "telefono": f"55 5010 01{offset}{idx}",
                    "activo": True,
                }
                for field, value in payload.items():
                    if getattr(miembro, field) != value:
                        setattr(miembro, field, value)
                        changed = True
                if changed:
                    miembro.save()

            CapacitacionDC3.all_objects.get_or_create(
                tenant=tenant,
                miembro=miembro,
                numero_dc3=f"DC3-{ciclo.anio}-{tipo[:3].upper()}-001",
                defaults={
                    "tenant": tenant,
                    "tipo_capacitacion": "Identificacion y prevencion de factores de riesgo psicosocial NOM-035",
                    "fecha": ciclo.fecha_inicio + timedelta(days=5),
                    "horas": 8,
                    "instructor": "Consultoria Demo Integral",
                },
            )

    def _create_policy(self, tenant: Tenant, ciclo: CicloNOM, admin_user: User) -> None:
        PoliticaPrevension.all_objects.get_or_create(
            tenant=tenant,
            ciclo=ciclo,
            defaults={
                "tenant": tenant,
                "titulo": "Politica de Prevencion de Factores de Riesgo Psicosocial",
                "contenido": POLICY_TEMPLATE.format(empresa=tenant.nombre),
                "estado": "vigente" if ciclo.estado != "iniciado" else "borrador",
                "firmante_nombre": admin_user.get_full_name(),
                "firmante_puesto": "Administrador de Empresa",
                "fecha_aprobacion": ciclo.fecha_inicio + timedelta(days=14),
            },
        )

    def _create_dissemination(self, tenant: Tenant, ciclo: CicloNOM, workers: list[Trabajador], offset: int) -> None:
        actividades = [
            ("correo", "Envio de politica NOM-035 y acuse digital", 160 + offset * 5),
            ("platica", "Sesion general sobre factores de riesgo psicosocial", 120 + offset * 8),
            ("cartel", "Campana visual en comedor, caseta y tablero operativo", 180),
            ("intranet", "Publicacion del micrositio de bienestar y canales de reporte", 175),
            ("reunion", "Charlas por turno con jefaturas y supervisores", 48 + offset * 6),
        ]
        responsable = worker_display_name(workers[9])
        for index, (tipo, titulo, participantes) in enumerate(actividades):
            ActividadDifusion.all_objects.get_or_create(
                tenant=tenant,
                ciclo=ciclo,
                titulo=f"{titulo} {ciclo.anio}",
                defaults={
                    "tenant": tenant,
                    "tipo": tipo,
                    "descripcion": f"Actividad demo del ciclo {ciclo.anio} para mantener evidencia de difusion.",
                    "fecha": ciclo.fecha_inicio + timedelta(days=18 + index * 12),
                    "num_participantes": participantes,
                    "responsable": responsable,
                },
            )

    def _create_action_plan(self, tenant: Tenant, ciclo: CicloNOM, workers: list[Trabajador], offset: int) -> None:
        plan, _ = PlanAccion.all_objects.get_or_create(
            tenant=tenant,
            ciclo=ciclo,
            defaults={
                "tenant": tenant,
                "descripcion": (
                    f"Plan anual de accion para el ciclo {ciclo.anio} con enfoque en liderazgo, "
                    "carga de trabajo, comunicacion por turnos y seguimiento de casos."
                ),
            },
        )

        acciones = [
            {
                "descripcion": "Balancear cargas de trabajo entre lineas de produccion y mantenimiento.",
                "tipo": "correctiva",
                "factor_riesgo": "Carga de trabajo y ritmo acelerado",
                "responsable": worker_display_name(workers[20]),
                "fecha_limite": ciclo.fecha_inicio + timedelta(days=75),
                "prioridad": "alta",
                "estado": "completado" if ciclo.anio <= 2025 else "en_progreso",
                "avance_notas": "Se redistribuyeron turnos y se ajustaron coberturas por celda.",
                "fecha_completado": ciclo.fecha_inicio + timedelta(days=70) if ciclo.anio <= 2025 else None,
            },
            {
                "descripcion": "Capacitar a supervisores en liderazgo operativo y retroalimentacion no violenta.",
                "tipo": "preventiva",
                "factor_riesgo": "Liderazgo negativo y relaciones de trabajo",
                "responsable": worker_display_name(workers[9]),
                "fecha_limite": ciclo.fecha_inicio + timedelta(days=95),
                "prioridad": "alta",
                "estado": "completado" if ciclo.anio == 2024 else "en_progreso",
                "avance_notas": "Programa de entrenamiento calendarizado y primera ronda impartida.",
                "fecha_completado": ciclo.fecha_inicio + timedelta(days=90) if ciclo.anio == 2024 else None,
            },
            {
                "descripcion": "Implementar pausas operativas y estiramientos guiados por turno.",
                "tipo": "preventiva",
                "factor_riesgo": "Fatiga y jornadas demandantes",
                "responsable": worker_display_name(workers[31]),
                "fecha_limite": ciclo.fecha_inicio + timedelta(days=60),
                "prioridad": "media",
                "estado": "completado" if ciclo.anio != 2026 else "en_progreso",
                "avance_notas": "Rutina visible en tableros y supervisada por seguridad e higiene.",
                "fecha_completado": ciclo.fecha_inicio + timedelta(days=58) if ciclo.anio != 2026 else None,
            },
            {
                "descripcion": "Abrir canal confidencial para reportes y seguimiento de incidentes psicosociales.",
                "tipo": "mejora",
                "factor_riesgo": "Violencia laboral y falta de canales de reporte",
                "responsable": worker_display_name(workers[10]),
                "fecha_limite": ciclo.fecha_inicio + timedelta(days=120),
                "prioridad": "media",
                "estado": "pendiente" if ciclo.anio == 2026 else "completado",
                "avance_notas": "Se definio flujo de atencion y responsables por caso.",
                "fecha_completado": ciclo.fecha_inicio + timedelta(days=118) if ciclo.anio != 2026 else None,
            },
            {
                "descripcion": "Reforzar comunicacion entre almacen, planeacion y produccion en cierre semanal.",
                "tipo": "mejora",
                "factor_riesgo": "Falta de control y claridad en el trabajo",
                "responsable": worker_display_name(workers[96]),
                "fecha_limite": ciclo.fecha_inicio + timedelta(days=88),
                "prioridad": "media",
                "estado": "completado" if ciclo.anio == 2024 else "en_progreso",
                "avance_notas": "Tablero de compromisos habilitado en reunion de los lunes.",
                "fecha_completado": ciclo.fecha_inicio + timedelta(days=84) if ciclo.anio == 2024 else None,
            },
            {
                "descripcion": "Monitorear casos de ausentismo vinculados con sobrecarga operativa.",
                "tipo": "correctiva",
                "factor_riesgo": "Sobrecarga y recuperacion insuficiente",
                "responsable": worker_display_name(workers[12]),
                "fecha_limite": ciclo.fecha_inicio + timedelta(days=145),
                "prioridad": "baja",
                "estado": "pendiente" if ciclo.anio == 2026 else "completado",
                "avance_notas": "Analisis mensual compartido entre RH y servicio medico.",
                "fecha_completado": ciclo.fecha_inicio + timedelta(days=140) if ciclo.anio != 2026 else None,
            },
        ]

        for accion in acciones:
            obj, created = AccionMedida.all_objects.get_or_create(
                tenant=tenant,
                plan=plan,
                descripcion=accion["descripcion"],
                defaults={**accion, "tenant": tenant},
            )
            if not created:
                changed = False
                for field, value in accion.items():
                    if getattr(obj, field) != value:
                        setattr(obj, field, value)
                        changed = True
                if changed:
                    obj.save()

    def _create_meetings(self, tenant: Tenant, ciclo: CicloNOM, workers: list[Trabajador], offset: int) -> None:
        reuniones = [
            {
                "tipo": "comite",
                "titulo": f"Instalacion del Comite NOM-035 {ciclo.anio}",
                "fecha": ciclo.fecha_inicio + timedelta(days=10),
                "lugar": "Sala Orion",
                "agenda": "Instalacion del comite, roles y calendario anual.",
                "minuta": "Se formalizo el comite y se aprobaron actividades iniciales del ciclo.",
                "asistentes": [0, 9, 24 + offset, 31, 96],
            },
            {
                "tipo": "capacitacion",
                "titulo": f"Capacitacion a mandos medios NOM-035 {ciclo.anio}",
                "fecha": ciclo.fecha_inicio + timedelta(days=24),
                "lugar": "Aula Sigma",
                "agenda": "Factores de riesgo, liderazgo y protocolo interno.",
                "minuta": "Participacion de supervisores de produccion, calidad y mantenimiento.",
                "asistentes": [9, 12, 20, 31, 45, 62, 108],
            },
            {
                "tipo": "seguimiento",
                "titulo": f"Revision trimestral del plan de accion {ciclo.anio}",
                "fecha": ciclo.fecha_inicio + timedelta(days=98),
                "lugar": "Sala Orion",
                "agenda": "Seguimiento de indicadores, avances y ajustes operativos.",
                "minuta": "Se revisaron acciones completadas, en progreso y medidas por reforzar.",
                "asistentes": [0, 9, 10, 20, 31, 96, 120],
            },
            {
                "tipo": "informativa",
                "titulo": f"Sesion informativa de resultados generales {ciclo.anio}",
                "fecha": ciclo.fecha_inicio + timedelta(days=160),
                "lugar": "Comedor principal",
                "agenda": "Presentacion de resultados agregados y mensajes preventivos.",
                "minuta": "Se compartieron hallazgos globales sin datos personales identificables.",
                "asistentes": [0, 9, 10, 24 + offset, 31, 45, 62, 96, 120, 150],
            },
        ]

        for data in reuniones:
            asistentes_idx = data.pop("asistentes")
            reunion, _ = Reunion.all_objects.get_or_create(
                tenant=tenant,
                ciclo=ciclo,
                titulo=data["titulo"],
                defaults={**data, "tenant": tenant},
            )
            for idx in asistentes_idx:
                worker = workers[idx]
                Asistente.all_objects.get_or_create(
                    tenant=tenant,
                    reunion=reunion,
                    nombre=worker_display_name(worker),
                    defaults={
                        "tenant": tenant,
                        "puesto": worker.puesto,
                        "firma_recibida": True,
                    },
                )

    def _create_evidence(self, tenant: Tenant, ciclo: CicloNOM, admin_user: User, offset: int) -> None:
        evidencias = [
            ("comite", f"acta-comite-{ciclo.anio}.txt", "Acta de instalacion del comite"),
            ("politica", f"politica-nom035-{ciclo.anio}.txt", "Politica publicada y aprobada"),
            ("difusion", f"difusion-nom035-{ciclo.anio}.txt", "Evidencia de actividades de difusion"),
            ("plan", f"plan-accion-{ciclo.anio}.txt", "Resumen ejecutivo del plan de accion"),
            ("aplicacion", f"seguimiento-cuestionarios-{ciclo.anio}.txt", "Seguimiento de aplicaciones y resultados"),
        ]

        for modulo, filename, nombre in evidencias:
            exists = EvidenciaDocumento.all_objects.filter(
                tenant=tenant,
                ciclo=ciclo,
                modulo=modulo,
                nombre=nombre,
            ).exists()
            if exists:
                continue

            contenido = (
                f"{nombre}\n"
                f"Tenant: {tenant.nombre}\n"
                f"Ciclo: {ciclo.anio}\n"
                f"Modulo: {modulo}\n"
                f"Documento sintetico para demo, generado automaticamente.\n"
                f"Lote: {offset + 1}\n"
            ).encode("utf-8")

            evidencia = EvidenciaDocumento.all_objects.create(
                tenant=tenant,
                ciclo=ciclo,
                modulo=modulo,
                nombre=nombre,
                descripcion=f"Archivo de evidencia demo del ciclo {ciclo.anio}.",
                tamanio=len(contenido),
                tipo_mime="text/plain",
                subido_por=admin_user,
            )
            evidencia.archivo.save(filename, ContentFile(contenido), save=True)

    def _create_applications(
        self,
        tenant: Tenant,
        ciclo: CicloNOM,
        workers: list[Trabajador],
        cuestionario: Cuestionario,
    ) -> None:
        cycle_config = next(item for item in CYCLES if item["anio"] == ciclo.anio)
        completed_goal = cycle_config["apps"]["completadas"]
        in_progress_goal = cycle_config["apps"]["en_progreso"]

        completadas = 0
        en_progreso = 0
        pendientes = 0

        for index, worker in enumerate(workers):
            app, _ = Aplicacion.all_objects.get_or_create(
                tenant=tenant,
                ciclo=ciclo,
                cuestionario=cuestionario,
                trabajador=worker,
                defaults={"tenant": tenant},
            )

            if index < completed_goal:
                if app.estado != "completado" or not hasattr(app, "resultado"):
                    self._reset_application(app)
                    self._complete_application(app, self._risk_profile(worker.area, index, ciclo.anio))
                completadas += 1
            elif index < completed_goal + in_progress_goal:
                if app.estado != "en_progreso":
                    self._reset_application(app)
                    self._create_partial_application(app, index)
                en_progreso += 1
            else:
                if app.estado != "pendiente" or app.respuestas.exists():
                    self._reset_application(app)
                pendientes += 1

        self._ok(
            f"Aplicaciones {ciclo.anio}: {completadas} completadas, "
            f"{en_progreso} en progreso, {pendientes} pendientes"
        )

    def _risk_profile(self, area: str, index: int, anio: int) -> str:
        if area in {"Recursos Humanos", "Direccion", "Servicio Medico"}:
            return "bajo"
        if area in {"Produccion", "Mantenimiento", "Logistica"}:
            if (index + anio) % 11 == 0:
                return "alto"
            return "medio"
        if (index + anio) % 17 == 0:
            return "alto"
        return "bajo"

    def _reset_application(self, app: Aplicacion) -> None:
        if hasattr(app, "resultado"):
            app.resultado.dominios.all().delete()
            app.resultado.delete()
        app.respuestas.all().delete()
        app.estado = "pendiente"
        app.fecha_completado = None
        app.save(update_fields=["estado", "fecha_completado"])

    def _create_partial_application(self, app: Aplicacion, seed_offset: int) -> None:
        preguntas = []
        for dominio in app.cuestionario.dominios.prefetch_related("preguntas").all():
            preguntas.extend(list(dominio.preguntas.all()))

        for idx, pregunta in enumerate(preguntas[:14]):
            valor = (seed_offset + idx) % 3
            RespuestaPregunta.objects.update_or_create(
                aplicacion=app,
                pregunta=pregunta,
                defaults={"tenant": app.tenant, "valor": valor},
            )

        app.estado = "en_progreso"
        app.fecha_completado = None
        app.save(update_fields=["estado", "fecha_completado"])

    def _complete_application(self, app: Aplicacion, perfil: str) -> None:
        values = {
            "bajo": {"regular": [0, 0, 1, 0, 1], "inversa": [4, 4, 3, 4, 3]},
            "medio": {"regular": [0, 1, 1, 2, 1], "inversa": [3, 3, 2, 3, 2]},
            "alto": {"regular": [1, 2, 2, 3, 2], "inversa": [2, 2, 1, 2, 1]},
        }
        profile_values = values[perfil]

        bulk = []
        for dominio in app.cuestionario.dominios.prefetch_related("preguntas").all():
            for pregunta in dominio.preguntas.all():
                options = profile_values["inversa"] if pregunta.inversa else profile_values["regular"]
                bulk.append(
                    RespuestaPregunta(
                        tenant=app.tenant,
                        aplicacion=app,
                        pregunta=pregunta,
                        valor=random.choice(options),
                    )
                )

        RespuestaPregunta.objects.bulk_create(bulk, ignore_conflicts=True)
        app.marcar_completado()
        app.refresh_from_db()
        result = calcular_resultado(app)
        resultado, _ = ResultadoAplicacion.objects.update_or_create(
            aplicacion=app,
            defaults={
                "puntaje_total": result["puntaje_total"],
                "puntaje_max": result["puntaje_max"],
                "categoria": result["categoria"],
            },
        )
        resultado.dominios.all().delete()
        ResultadoDominio.objects.bulk_create(
            [
                ResultadoDominio(
                    resultado=resultado,
                    dominio_id=item["dominio_id"],
                    puntaje=item["puntaje"],
                    puntaje_max=item["puntaje_max"],
                    categoria=item["categoria"],
                )
                for item in result["dominios"]
            ]
        )

    def _print_summary(self) -> None:
        sep = "-" * 62
        self.stdout.write("\n" + sep)
        self.stdout.write(self.style.SUCCESS("TENANT DEMO MASIVO LISTO"))
        self.stdout.write(sep)
        self.stdout.write(f"  Tenant   : {TENANT_DATA['nombre']}")
        self.stdout.write(f"  RFC      : {TENANT_DATA['rfc']}")
        self.stdout.write(f"  Admin    : {ADMIN_USER['email']}")
        self.stdout.write(f"  Password : {ADMIN_USER['password']}")
        self.stdout.write("  Super    : superadmin@intra.com / Admin123!")
        self.stdout.write("  Nota     : Datos sinteticos para demo; no corresponden a personas reales.")
        self.stdout.write(sep)

    def _ok(self, message: str) -> None:
        self.stdout.write(self.style.SUCCESS(f"[OK] {message}"))

    def _skip(self, message: str) -> None:
        self.stdout.write(self.style.WARNING(f"[--] {message}"))
