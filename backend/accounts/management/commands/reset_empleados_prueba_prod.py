"""
Resetea los empleados del tenant PRUEBA en produccion.

Acciones:
  1. Busca el tenant por RFC 'PRU010101AA1'
  2. Elimina TODOS sus empleados y datos de encuestas asociados
  3. Crea empleados frescos con prefijo PRUEBA, sin encuestas contestadas

Uso:
    python manage.py reset_empleados_prueba_prod --confirm
"""
import random
from django.core.management.base import BaseCommand
from django.db import transaction

from tenants.models import Tenant
from m00_onboarding.models import Trabajador

TENANT_RFC = 'PRU010101AA1'
SEED = 11

NOMBRES = [
    'Alejandro', 'Ana', 'Andres', 'Beatriz', 'Carlos', 'Carmen', 'Claudia',
    'Daniel', 'Daniela', 'Eduardo', 'Elena', 'Fernando', 'Gabriel', 'Gabriela',
    'Hugo', 'Isabel', 'Javier', 'Jessica', 'Jorge', 'Jose', 'Juan', 'Laura',
    'Leticia', 'Luis', 'Luisa', 'Manuel', 'Maria', 'Mario', 'Martha', 'Miguel',
    'Monica', 'Oscar', 'Patricia', 'Pedro', 'Rafael', 'Ricardo', 'Roberto',
    'Rosa', 'Sandra', 'Santiago', 'Sara', 'Sergio', 'Sofia', 'Teresa', 'Valeria',
    'Victor', 'Veronica', 'Ximena', 'Yolanda', 'Zulema',
]

AP_PATERNO = [
    'Aguilar', 'Castro', 'Cruz', 'Diaz', 'Flores', 'Garcia', 'Gomez',
    'Gonzalez', 'Gutierrez', 'Hernandez', 'Jimenez', 'Lopez', 'Lozano',
    'Martinez', 'Medina', 'Mendoza', 'Morales', 'Moreno', 'Munoz', 'Ortega',
    'Ortiz', 'Perez', 'Ramos', 'Ramirez', 'Reyes', 'Rivera', 'Rodriguez',
    'Romero', 'Ruiz', 'Sanchez', 'Santos', 'Soto', 'Torres', 'Vargas',
    'Vega', 'Velazquez',
]

# (area, tipo_puesto, cantidad)
AREAS = [
    ('Produccion',      'Operativo',      20),
    ('Produccion',      'Tecnico',         8),
    ('Produccion',      'Supervisor',      4),
    ('Ventas',          'Operativo',      15),
    ('Ventas',          'Supervisor',      4),
    ('Ventas',          'Gerente',         2),
    ('Administracion',  'Administrativo', 10),
    ('Administracion',  'Gerente',         2),
    ('TI',              'Tecnico',         8),
    ('TI',              'Gerente',         2),
    ('RRHH',            'Administrativo',  6),
    ('RRHH',            'Supervisor',      3),
    ('Operaciones',     'Operativo',      12),
    ('Operaciones',     'Supervisor',      4),
    ('Logistica',       'Operativo',       6),
    ('Calidad',         'Tecnico',         4),
]


class Command(BaseCommand):
    help = 'Borra todos los empleados del tenant PRUEBA y los recrea sin encuestas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirmar la operación sin prompt interactivo.',
        )

    def handle(self, *args, **options):
        try:
            tenant = Tenant.objects.get(rfc=TENANT_RFC)
        except Tenant.DoesNotExist:
            self.stderr.write(self.style.ERROR(
                f'Tenant con RFC "{TENANT_RFC}" no encontrado.'
            ))
            return

        self.stdout.write(f'Tenant encontrado: "{tenant.nombre}" (ID {tenant.id})')

        if not options['confirm']:
            confirm = input(
                f'\n¿Borrar TODOS los empleados de "{tenant.nombre}" y recargar con PRUEBA? [s/N] '
            )
            if confirm.lower() != 's':
                self.stdout.write(self.style.WARNING('Operación cancelada.'))
                return

        total_empleados = sum(c for _, _, c in AREAS)

        with transaction.atomic():
            # ── 1. Limpiar encuestas asociadas a trabajadores del tenant ────
            from m05_questionnaires.models import Aplicacion, RespuestaPregunta, AplicacionFoto
            from m06_results.models import ResultadoAplicacion

            apps_qs = Aplicacion.objects.filter(tenant=tenant)
            n_resp = RespuestaPregunta.objects.filter(tenant=tenant).delete()[0]
            n_fotos = AplicacionFoto.objects.filter(tenant=tenant).delete()[0]
            # ResultadoDominio se borra en cascada con ResultadoAplicacion
            n_resultados = ResultadoAplicacion.objects.filter(
                aplicacion__in=apps_qs
            ).delete()[0]
            n_apps = apps_qs.delete()[0]

            # ── 2. Borrar todos los trabajadores del tenant ─────────────────
            n_trabajadores = Trabajador.objects.filter(tenant=tenant).delete()[0]

            self.stdout.write(
                f'Eliminados: {n_trabajadores} trabajadores, '
                f'{n_apps} aplicaciones, '
                f'{n_resp} respuestas, '
                f'{n_resultados} resultados, '
                f'{n_fotos} fotos'
            )

            # ── 3. Actualizar num_trabajadores si hace falta ─────────────────
            if tenant.num_trabajadores < total_empleados:
                tenant.num_trabajadores = total_empleados + 20
                tenant.save(update_fields=['num_trabajadores'])
                self.stdout.write(
                    f'num_trabajadores actualizado a {tenant.num_trabajadores}'
                )

            # ── 4. Crear nuevos empleados PRUEBA sin encuestas ───────────────
            random.seed(SEED)
            nombres_usados = set()
            idx = 0
            trabajadores = []

            for area, tipo_puesto, cantidad in AREAS:
                for _ in range(cantidad):
                    while True:
                        nombre = random.choice(NOMBRES)
                        ap = random.choice(AP_PATERNO)
                        clave = f'{nombre}{ap}'
                        if clave not in nombres_usados:
                            nombres_usados.add(clave)
                            break

                    idx += 1
                    trabajadores.append(Trabajador(
                        tenant=tenant,
                        nombre=f'PRUEBA {nombre}',
                        apellido_paterno=ap,
                        num_empleado=f'PRUEBA-{idx:03d}',
                        area=area,
                        tipo_puesto=tipo_puesto,
                        tipo_contratacion=random.choice(['planta', 'eventual', 'subcontratado']),
                        tipo_jornada=random.choice(['diurno', 'mixto', 'tiempo_completo', 'nocturno']),
                        sexo=random.choice(['M', 'F']),
                        edad=random.randint(22, 55),
                        activo=True,
                    ))

            Trabajador.objects.bulk_create(trabajadores)

        self.stdout.write(self.style.SUCCESS(
            f'\nOK: {idx} empleados PRUEBA creados en "{tenant.nombre}" sin encuestas contestadas.'
        ))
        self.stdout.write('Distribucion por area:')
        for area, tipo_puesto, cantidad in AREAS:
            self.stdout.write(f'  {area:20s} / {tipo_puesto:15s}: {cantidad}')
