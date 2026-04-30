"""
Crea el tenant de demo "Orbita SIT" con datos realistas.
Idempotente: puede ejecutarse varias veces sin duplicar registros.

Uso:
    python manage.py seed_orbita_demo
"""
import random
from datetime import date, timedelta

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
from m08_attendance.models import Asistente, Reunion
from tenants.models import Tenant

# ---------------------------------------------------------------------------
# Datos del tenant
# ---------------------------------------------------------------------------

TENANT_DATA = {
    'nombre': 'Orbita SIT',
    'rfc': 'ORS900215KL3',
    'giro': 'Desarrollo de software y soluciones tecnológicas',
    'num_trabajadores': 25,
    'telefono_contacto': '(55) 4170-3820',
    'sitio_web': 'https://www.orbitasit.mx',
    'direccion': 'Av. Insurgentes Sur 1602, Piso 8, Col. Crédito Constructor, Benito Juárez, CDMX, C.P. 03940',
}

ADMIN_DATA = {
    'email': 'admin@orbitasit.mx',
    'username': 'orbita_admin',
    'first_name': 'Ricardo',
    'last_name': 'Domínguez Serrano',
    'password': 'OrbitaDemo2025!',
}

# ---------------------------------------------------------------------------
# Trabajadores
# ---------------------------------------------------------------------------

TRABAJADORES = [
    {
        'nombre': 'Ricardo',
        'apellido_paterno': 'Domínguez',
        'apellido_materno': 'Serrano',
        'num_empleado': 'OST-001',
        'email': 'r.dominguez@orbitasit.mx',
        'puesto': 'Director General',
        'area': 'Dirección',
        'tipo_contratacion': 'planta',
    },
    {
        'nombre': 'Laura',
        'apellido_paterno': 'Ramírez',
        'apellido_materno': 'Castro',
        'num_empleado': 'OST-002',
        'email': 'l.ramirez@orbitasit.mx',
        'puesto': 'Project Manager',
        'area': 'PMO',
        'tipo_contratacion': 'planta',
    },
    {
        'nombre': 'Carlos',
        'apellido_paterno': 'Hernández',
        'apellido_materno': 'Vega',
        'num_empleado': 'OST-003',
        'email': 'c.hernandez@orbitasit.mx',
        'puesto': 'Gerente de Desarrollo',
        'area': 'Tecnología',
        'tipo_contratacion': 'planta',
    },
    {
        'nombre': 'Ana',
        'apellido_paterno': 'Martínez',
        'apellido_materno': 'López',
        'num_empleado': 'OST-004',
        'email': 'a.martinez@orbitasit.mx',
        'puesto': 'Desarrolladora Senior',
        'area': 'Tecnología',
        'tipo_contratacion': 'planta',
    },
    {
        'nombre': 'Jorge',
        'apellido_paterno': 'Torres',
        'apellido_materno': 'Jiménez',
        'num_empleado': 'OST-005',
        'email': 'j.torres@orbitasit.mx',
        'puesto': 'DevOps Engineer',
        'area': 'Infraestructura',
        'tipo_contratacion': 'planta',
    },
    {
        'nombre': 'María',
        'apellido_paterno': 'González',
        'apellido_materno': 'Reyes',
        'num_empleado': 'OST-006',
        'email': 'm.gonzalez@orbitasit.mx',
        'puesto': 'Diseñadora UX/UI',
        'area': 'Diseño',
        'tipo_contratacion': 'planta',
    },
    {
        'nombre': 'Diego',
        'apellido_paterno': 'Flores',
        'apellido_materno': 'Mendoza',
        'num_empleado': 'OST-007',
        'email': 'd.flores@orbitasit.mx',
        'puesto': 'QA Engineer',
        'area': 'Calidad',
        'tipo_contratacion': 'eventual',
    },
    {
        'nombre': 'Sofía',
        'apellido_paterno': 'Ruiz',
        'apellido_materno': 'Gutiérrez',
        'num_empleado': 'OST-008',
        'email': 's.ruiz@orbitasit.mx',
        'puesto': 'Desarrolladora Frontend',
        'area': 'Tecnología',
        'tipo_contratacion': 'planta',
    },
    {
        'nombre': 'Alejandro',
        'apellido_paterno': 'Morales',
        'apellido_materno': 'Peña',
        'num_empleado': 'OST-009',
        'email': 'a.morales@orbitasit.mx',
        'puesto': 'Analista de Seguridad',
        'area': 'Infraestructura',
        'tipo_contratacion': 'planta',
    },
    {
        'nombre': 'Valentina',
        'apellido_paterno': 'Cruz',
        'apellido_materno': 'Ibáñez',
        'num_empleado': 'OST-010',
        'email': 'v.cruz@orbitasit.mx',
        'puesto': 'Coordinadora de RH',
        'area': 'Recursos Humanos',
        'tipo_contratacion': 'planta',
    },
    {
        'nombre': 'Fernando',
        'apellido_paterno': 'Sánchez',
        'apellido_materno': 'Olvera',
        'num_empleado': 'OST-011',
        'email': 'f.sanchez@orbitasit.mx',
        'puesto': 'Desarrollador Backend',
        'area': 'Tecnología',
        'tipo_contratacion': 'planta',
    },
    {
        'nombre': 'Gabriela',
        'apellido_paterno': 'Vargas',
        'apellido_materno': 'Núñez',
        'num_empleado': 'OST-012',
        'email': 'g.vargas@orbitasit.mx',
        'puesto': 'Ejecutiva de Ventas',
        'area': 'Comercial',
        'tipo_contratacion': 'planta',
    },
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _categoria(puntaje, puntaje_max):
    pct = puntaje / puntaje_max if puntaje_max else 0
    if pct <= 0.25:
        return 'bajo'
    if pct <= 0.50:
        return 'medio'
    if pct <= 0.75:
        return 'alto'
    return 'muy_alto'


def _puntaje_realista(puntaje_max, perfil='normal'):
    """Genera un puntaje realista según el perfil de riesgo."""
    if perfil == 'bajo':
        return random.randint(0, int(puntaje_max * 0.25))
    if perfil == 'medio':
        return random.randint(int(puntaje_max * 0.20), int(puntaje_max * 0.50))
    # normal: mezcla de bajo y medio (empresa de TI bien gestionada)
    return random.randint(int(puntaje_max * 0.10), int(puntaje_max * 0.45))


# ---------------------------------------------------------------------------
# Comando
# ---------------------------------------------------------------------------

class Command(BaseCommand):
    help = 'Crea el tenant de demo Orbita SIT con datos realistas'

    def handle(self, *args, **options):
        random.seed(42)  # resultados reproducibles

        with transaction.atomic():
            super_admin = self._ensure_super_admin()
            tenant      = self._create_tenant(super_admin)
            _           = self._create_admin(tenant)
            trabajadores = self._create_trabajadores(tenant)
            ciclo       = self._create_ciclo(tenant)
            self._create_comite(tenant, ciclo, trabajadores)
            self._create_politica(tenant, ciclo)
            self._create_difusion(tenant, ciclo)
            self._create_plan_accion(tenant, ciclo, trabajadores)
            self._create_reuniones(tenant, ciclo, trabajadores)
            self._create_aplicaciones(tenant, ciclo, trabajadores)

        self._print_summary()

    # ------------------------------------------------------------------
    # Pasos
    # ------------------------------------------------------------------

    def _ensure_super_admin(self):
        admin, created = User.objects.get_or_create(
            email='superadmin@intra.com',
            defaults={
                'username': 'superadmin',
                'first_name': 'Super',
                'last_name': 'Admin',
                'rol': User.SUPER_ADMIN,
                'is_active': True,
                'is_staff': True,
            },
        )
        if created:
            admin.set_password('Admin123!')
            admin.save()
            self._ok('Super admin creado')
        else:
            self._skip('Super admin ya existe')
        return admin

    def _create_tenant(self, super_admin):
        tenant, created = Tenant.objects.get_or_create(
            rfc=TENANT_DATA['rfc'],
            defaults={
                'nombre': TENANT_DATA['nombre'],
                'giro': TENANT_DATA['giro'],
                'num_trabajadores': TENANT_DATA['num_trabajadores'],
                'consultor': super_admin,
                'telefono_contacto': TENANT_DATA['telefono_contacto'],
                'sitio_web': TENANT_DATA['sitio_web'],
                'direccion': TENANT_DATA['direccion'],
            },
        )
        if created:
            self._ok(f'Tenant "{tenant.nombre}" creado')
        else:
            self._skip(f'Tenant "{tenant.nombre}" ya existe')
        return tenant

    def _create_admin(self, tenant):
        admin, created = User.objects.get_or_create(
            email=ADMIN_DATA['email'],
            defaults={
                'username': ADMIN_DATA['username'],
                'first_name': ADMIN_DATA['first_name'],
                'last_name': ADMIN_DATA['last_name'],
                'rol': User.TENANT_ADMIN,
                'tenant': tenant,
                'is_active': True,
            },
        )
        if created:
            admin.set_password(ADMIN_DATA['password'])
            admin.save()
            self._ok('Tenant admin creado')
        else:
            self._skip('Tenant admin ya existe')
        return admin

    def _create_trabajadores(self, tenant):
        creados = []
        for data in TRABAJADORES:
            obj, created = Trabajador.all_objects.get_or_create(
                tenant=tenant,
                num_empleado=data['num_empleado'],
                defaults={**data, 'tenant': tenant},
            )
            creados.append(obj)
            if created:
                self._ok(f'  Trabajador: {obj.nombre_completo}')
        self._ok(f'{len(creados)} trabajadores listos')
        return creados

    def _create_ciclo(self, tenant):
        ciclo, created = CicloNOM.all_objects.get_or_create(
            tenant=tenant,
            anio=2025,
            defaults={
                'tenant': tenant,
                'estado': 'en_progreso',
                'fecha_inicio': date(2025, 1, 6),
                'notas': 'Ciclo de implementación NOM-035 — ejercicio 2025.',
            },
        )
        if created:
            self._ok('Ciclo NOM-035 2025 creado')
        else:
            self._skip('Ciclo 2025 ya existe')
        return ciclo

    def _create_comite(self, tenant, ciclo, trabajadores):
        comite, created = ComiteNOM.all_objects.get_or_create(
            tenant=tenant,
            ciclo=ciclo,
            defaults={
                'tenant': tenant,
                'fecha_constitucion': date(2025, 1, 20),
                'numero_acta': 'ACTA-2025-001',
                'observaciones': (
                    'Comité constituido conforme al Art. 15 de la NOM-035-STPS-2018. '
                    'Todos los miembros firmaron el acta de constitución.'
                ),
            },
        )
        if not created:
            self._skip('Comité ya existe')
            return comite

        self._ok('Comité NOM-035 creado')

        miembros_data = [
            {
                'nombre': 'Ricardo Domínguez Serrano',
                'puesto': 'Director General',
                'tipo': 'presidente',
                'email': 'r.dominguez@orbitasit.mx',
                'telefono': '(55) 4170-3820',
            },
            {
                'nombre': 'Laura Ramírez Castro',
                'puesto': 'Project Manager',
                'tipo': 'secretario',
                'email': 'l.ramirez@orbitasit.mx',
                'telefono': '(55) 4170-3821',
            },
            {
                'nombre': 'Valentina Cruz Ibáñez',
                'puesto': 'Coordinadora de RH',
                'tipo': 'vocal',
                'email': 'v.cruz@orbitasit.mx',
                'telefono': '(55) 4170-3825',
            },
        ]
        for m in miembros_data:
            miembro = MiembroComite.all_objects.create(
                tenant=tenant,
                comite=comite,
                **m,
            )
            self._ok(f'  Miembro: {miembro.nombre} ({miembro.get_tipo_display()})')

            # Capacitación DC3 para cada miembro
            CapacitacionDC3.all_objects.create(
                tenant=tenant,
                miembro=miembro,
                tipo_capacitacion='Identificación y prevención de factores de riesgo psicosocial NOM-035',
                fecha=date(2025, 1, 15),
                horas=8,
                instructor='Lic. Mariana Solís Pacheco',
                numero_dc3=f'DC3-2025-{miembro.tipo[:3].upper()}-001',
            )

        return comite

    def _create_politica(self, tenant, ciclo):
        _, created = PoliticaPrevension.all_objects.get_or_create(
            tenant=tenant,
            ciclo=ciclo,
            defaults={
                'tenant': tenant,
                'titulo': 'Política de Prevención de Factores de Riesgo Psicosocial',
                'contenido': (
                    'En Orbita SIT, S. de R.L. de C.V., nos comprometemos a promover un entorno '
                    'laboral favorable para todos nuestros colaboradores, garantizando condiciones '
                    'de trabajo que prevengan los factores de riesgo psicosocial y la violencia '
                    'laboral, en cumplimiento de la NOM-035-STPS-2018.\n\n'
                    'Para ello nos comprometemos a:\n'
                    '1. Identificar, analizar y prevenir los factores de riesgo psicosocial.\n'
                    '2. Promover un entorno organizacional favorable mediante la comunicación '
                    'abierta, el reconocimiento al desempeño y la distribución equitativa de '
                    'cargas de trabajo.\n'
                    '3. Atender las prácticas opuestas al entorno organizacional favorable y '
                    'los actos de violencia laboral.\n'
                    '4. Revisar y actualizar esta política anualmente o ante cambios '
                    'significativos en la organización.'
                ),
                'estado': 'vigente',
                'firmante_nombre': 'Ricardo Domínguez Serrano',
                'firmante_puesto': 'Director General',
                'fecha_aprobacion': date(2025, 1, 27),
            },
        )
        if created:
            self._ok('Política de prevención creada')
        else:
            self._skip('Política ya existe')

    def _create_difusion(self, tenant, ciclo):
        actividades = [
            {
                'tipo': 'platica',
                'titulo': 'Inducción NOM-035: Factores de Riesgo Psicosocial',
                'descripcion': (
                    'Sesión informativa para todo el personal sobre el alcance, '
                    'objetivos y obligaciones de la NOM-035-STPS-2018.'
                ),
                'fecha': date(2025, 2, 10),
                'num_participantes': 25,
                'responsable': 'Valentina Cruz Ibáñez',
            },
            {
                'tipo': 'correo',
                'titulo': 'Comunicado: Política de Prevención de Factores de Riesgo Psicosocial',
                'descripcion': (
                    'Difusión electrónica de la política aprobada a todos los '
                    'colaboradores con acuse de recibo vía correo.'
                ),
                'fecha': date(2025, 2, 3),
                'num_participantes': 25,
                'responsable': 'Valentina Cruz Ibáñez',
            },
            {
                'tipo': 'cartel',
                'titulo': 'Carteles informativos NOM-035 en áreas comunes',
                'descripcion': (
                    'Colocación de material impreso en comedor, sala de juntas y '
                    'recepción con información sobre la norma y canales de reporte.'
                ),
                'fecha': date(2025, 2, 17),
                'num_participantes': 25,
                'responsable': 'Laura Ramírez Castro',
            },
        ]
        for data in actividades:
            exists = ActividadDifusion.all_objects.filter(
                tenant=tenant, ciclo=ciclo, titulo=data['titulo']
            ).exists()
            if not exists:
                ActividadDifusion.all_objects.create(tenant=tenant, ciclo=ciclo, **data)
                self._ok(f'  Difusión: {data["titulo"][:55]}')
        self._ok('Actividades de difusión listas')

    def _create_plan_accion(self, tenant, ciclo, trabajadores):
        plan, created = PlanAccion.all_objects.get_or_create(
            tenant=tenant,
            ciclo=ciclo,
            defaults={
                'tenant': tenant,
                'descripcion': (
                    'Plan de acción para la atención de los factores de riesgo psicosocial '
                    'identificados durante el ciclo 2025 en Orbita SIT.'
                ),
            },
        )
        if not created:
            self._skip('Plan de acción ya existe')
            return plan

        self._ok('Plan de acción creado')

        acciones = [
            {
                'descripcion': (
                    'Implementar programa de pausas activas de 10 minutos a media mañana '
                    'y media tarde para reducir la fatiga generada por trabajo prolongado '
                    'frente a pantallas.'
                ),
                'tipo': 'preventiva',
                'factor_riesgo': 'Carga de trabajo / jornada prolongada frente a pantalla',
                'responsable': 'Valentina Cruz Ibáñez',
                'fecha_limite': date(2025, 4, 30),
                'prioridad': 'alta',
                'estado': 'en_progreso',
                'avance_notas': 'Se difundió el programa en febrero; participación del 80% del personal.',
            },
            {
                'descripcion': (
                    'Organizar taller de gestión del estrés y técnicas de mindfulness '
                    'para todo el personal, con sesiones mensuales de 2 horas.'
                ),
                'tipo': 'preventiva',
                'factor_riesgo': 'Estrés laboral / carga mental elevada',
                'responsable': 'Laura Ramírez Castro',
                'fecha_limite': date(2025, 6, 30),
                'prioridad': 'media',
                'estado': 'pendiente',
                'avance_notas': '',
            },
            {
                'descripcion': (
                    'Revisar y redistribuir las cargas de trabajo en el área de Tecnología '
                    'para equilibrar los proyectos asignados por colaborador y evitar '
                    'sobrecargas recurrentes.'
                ),
                'tipo': 'correctiva',
                'factor_riesgo': 'Distribución inequitativa de tareas / horas extra excesivas',
                'responsable': 'Carlos Hernández Vega',
                'fecha_limite': date(2025, 5, 15),
                'prioridad': 'alta',
                'estado': 'en_progreso',
                'avance_notas': (
                    'Se realizó diagnóstico de carga con los líderes de proyecto el 03/Mar. '
                    'Propuesta de redistribución en revisión con dirección.'
                ),
            },
            {
                'descripcion': (
                    'Establecer protocolo formal de reporte y atención de actos de violencia '
                    'laboral, incluyendo canal confidencial de denuncia y tiempos de respuesta.'
                ),
                'tipo': 'mejora',
                'factor_riesgo': 'Violencia laboral / hostigamiento',
                'responsable': 'Valentina Cruz Ibáñez',
                'fecha_limite': date(2025, 7, 31),
                'prioridad': 'media',
                'estado': 'pendiente',
                'avance_notas': '',
            },
        ]
        for a in acciones:
            AccionMedida.all_objects.create(tenant=tenant, plan=plan, **a)
            self._ok(f'  Acción: {a["descripcion"][:60]}…')

        return plan

    def _create_reuniones(self, tenant, ciclo, trabajadores):
        reuniones_data = [
            {
                'tipo': 'comite',
                'titulo': 'Sesión de constitución del Comité NOM-035',
                'fecha': date(2025, 1, 20),
                'lugar': 'Sala de Juntas "Kuiper" — Piso 8',
                'agenda': (
                    '1. Presentación de la NOM-035-STPS-2018.\n'
                    '2. Integración y elección de miembros del comité.\n'
                    '3. Firma del acta de constitución.\n'
                    '4. Calendarización de actividades del ciclo 2025.'
                ),
                'minuta': (
                    'Se constituyó el Comité NOM-035 con tres integrantes: presidente, '
                    'secretario y vocal. Todos firmaron el acta folio ACTA-2025-001. '
                    'Se aprobó el calendario de aplicación de cuestionarios para el mes de marzo.'
                ),
                'asistentes': [
                    ('Ricardo Domínguez Serrano', 'Director General'),
                    ('Laura Ramírez Castro', 'Project Manager'),
                    ('Valentina Cruz Ibáñez', 'Coordinadora de RH'),
                    ('Carlos Hernández Vega', 'Gerente de Desarrollo'),
                ],
            },
            {
                'tipo': 'capacitacion',
                'titulo': 'Capacitación en identificación de factores de riesgo psicosocial',
                'fecha': date(2025, 1, 15),
                'lugar': 'Sala de Capacitación "Vega" — Piso 8',
                'agenda': (
                    '1. Marco legal NOM-035-STPS-2018.\n'
                    '2. Definición de factores de riesgo psicosocial.\n'
                    '3. Obligaciones del patrón y del trabajador.\n'
                    '4. Proceso de aplicación del cuestionario.\n'
                    '5. Entrega de constancias DC-3.'
                ),
                'minuta': (
                    'Capacitación impartida por la Lic. Mariana Solís Pacheco. '
                    'Asistieron los tres miembros del comité. Se entregaron constancias DC-3 '
                    'folio DC3-2025-PRE-001, DC3-2025-SEC-001 y DC3-2025-VOC-001.'
                ),
                'asistentes': [
                    ('Ricardo Domínguez Serrano', 'Director General'),
                    ('Laura Ramírez Castro', 'Project Manager'),
                    ('Valentina Cruz Ibáñez', 'Coordinadora de RH'),
                    ('Mariana Solís Pacheco', 'Instructora Externa'),
                ],
            },
            {
                'tipo': 'seguimiento',
                'titulo': 'Primera reunión de seguimiento al Plan de Acción',
                'fecha': date(2025, 4, 7),
                'lugar': 'Sala de Juntas "Kuiper" — Piso 8',
                'agenda': (
                    '1. Avance de acciones preventivas del Plan 2025.\n'
                    '2. Resultados preliminares del programa de pausas activas.\n'
                    '3. Revisión de redistribución de cargas en Tecnología.\n'
                    '4. Próximos pasos y compromisos.'
                ),
                'minuta': (
                    'Se reportó 80% de participación en pausas activas. El área de Tecnología '
                    'presentó propuesta de redistribución de carga. Se acordó presentar '
                    'protocolo de violencia laboral en reunión de junio.'
                ),
                'asistentes': [
                    ('Ricardo Domínguez Serrano', 'Director General'),
                    ('Laura Ramírez Castro', 'Project Manager'),
                    ('Valentina Cruz Ibáñez', 'Coordinadora de RH'),
                    ('Carlos Hernández Vega', 'Gerente de Desarrollo'),
                    ('Ana Martínez López', 'Desarrolladora Senior'),
                ],
            },
        ]

        for data in reuniones_data:
            asistentes_raw = data.pop('asistentes')
            exists = Reunion.all_objects.filter(
                tenant=tenant, ciclo=ciclo, titulo=data['titulo']
            ).exists()
            if not exists:
                reunion = Reunion.all_objects.create(tenant=tenant, ciclo=ciclo, **data)
                self._ok(f'  Reunión: {reunion.titulo[:55]}')
                for nombre, puesto in asistentes_raw:
                    Asistente.all_objects.create(
                        tenant=tenant,
                        reunion=reunion,
                        nombre=nombre,
                        puesto=puesto,
                        firma_recibida=True,
                    )

        self._ok('Reuniones y asistentes listos')

    def _create_aplicaciones(self, tenant, ciclo, trabajadores):
        cuestionarios = list(Cuestionario.objects.filter(clave__in=['I', 'III']))
        if not cuestionarios:
            self.stdout.write(self.style.WARNING(
                'No hay cuestionarios en BD. Ejecuta primero: python manage.py seed_cuestionarios'
            ))
            return

        # 25 trabajadores → aplica Guía I y Guía III
        # Distribución realista: mayoría bajo/medio, 1-2 casos alto
        perfiles = ['bajo', 'medio', 'bajo', 'alto', 'medio',
                    'bajo', 'medio', 'alto', 'bajo', 'medio',
                    'bajo', 'bajo']
        creadas = completadas = 0

        for i, trabajador in enumerate(trabajadores):
            perfil = perfiles[i % len(perfiles)]
            for cuestionario in cuestionarios:
                app, created = Aplicacion.all_objects.get_or_create(
                    tenant=tenant,
                    ciclo=ciclo,
                    cuestionario=cuestionario,
                    trabajador=trabajador,
                    defaults={'tenant': tenant},
                )
                if created:
                    creadas += 1

                # Completar 8 de 12 trabajadores (primeros 8)
                if i < 8 and app.estado != 'completado':
                    self._completar_aplicacion(app, cuestionario, perfil)
                    completadas += 1

        self._ok(f'Aplicaciones: {creadas} creadas, {completadas} completadas con resultados')

    def _completar_aplicacion(self, app, cuestionario, perfil):
        """
        Crea RespuestaPregunta con valores coherentes al perfil de riesgo,
        luego usa el motor oficial (calcular_resultado) para obtener puntajes
        y categorías. Así el endpoint /calcular siempre produce resultados
        consistentes al recalcular.
        """
        # Valores calibrados contra umbrales NOM-035 (scoring.py).
        # Guía III global: ≤20 bajo, 21-45 medio, 46-70 alto, 71+ muy_alto (40 preg × 4 = 160 max)
        # Regular: valor alto = más riesgo;  Inversa: valor bajo = más riesgo (puntaje = 4-valor)
        VALORES = {
            'bajo':  {'regular': [0, 0, 0, 1, 0], 'inversa': [4, 4, 3, 4, 4]},   # avg puntaje ~0.2/preg
            'medio': {'regular': [0, 1, 1, 1, 1], 'inversa': [3, 3, 4, 3, 3]},   # avg puntaje ~0.8/preg
            'alto':  {'regular': [1, 1, 2, 2, 1], 'inversa': [2, 3, 2, 2, 3]},   # avg puntaje ~1.5/preg
        }
        pool = VALORES.get(perfil, VALORES['bajo'])

        respuestas_bulk = []
        for dominio in cuestionario.dominios.prefetch_related('preguntas').all():
            for pregunta in dominio.preguntas.all():
                opciones = pool['inversa'] if pregunta.inversa else pool['regular']
                valor = random.choice(opciones)
                respuestas_bulk.append(
                    RespuestaPregunta(
                        tenant=app.tenant,
                        aplicacion=app,
                        pregunta=pregunta,
                        valor=valor,
                    )
                )

        if not respuestas_bulk:
            return

        RespuestaPregunta.objects.bulk_create(respuestas_bulk, ignore_conflicts=True)
        app.marcar_completado()

        # Recalcular con el motor oficial usando las respuestas recién creadas
        app.refresh_from_db()
        datos = calcular_resultado(app)

        resultado, _ = ResultadoAplicacion.objects.update_or_create(
            aplicacion=app,
            defaults={
                'puntaje_total': datos['puntaje_total'],
                'puntaje_max':   datos['puntaje_max'],
                'categoria':     datos['categoria'],
            },
        )
        resultado.dominios.all().delete()
        ResultadoDominio.objects.bulk_create([
            ResultadoDominio(
                resultado=resultado,
                dominio_id=d['dominio_id'],
                puntaje=d['puntaje'],
                puntaje_max=d['puntaje_max'],
                categoria=d['categoria'],
            )
            for d in datos['dominios']
        ])

    # ------------------------------------------------------------------
    # Utilidades de salida
    # ------------------------------------------------------------------

    def _ok(self, msg):
        self.stdout.write(self.style.SUCCESS(f'[OK] {msg}'))

    def _skip(self, msg):
        self.stdout.write(self.style.WARNING(f'[--] {msg}'))

    def _print_summary(self):
        sep = '-' * 50
        self.stdout.write('\n' + sep)
        self.stdout.write(self.style.SUCCESS('DEMO ORBITA SIT LISTA'))
        self.stdout.write(sep)
        self.stdout.write(f'  Tenant   : Orbita SIT  (RFC: {TENANT_DATA["rfc"]})')
        self.stdout.write(f'  Admin    : {ADMIN_DATA["email"]}')
        self.stdout.write(f'  Password : {ADMIN_DATA["password"]}')
        self.stdout.write(f'  Super    : superadmin@intra.com / Admin123!')
        self.stdout.write(sep)
