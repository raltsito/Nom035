"""
Carga empleados de prueba en el tenant local (ID 1).
- Nombres con "PRUEBA " como prefijo en el campo nombre
- Sin encuestas ni aplicaciones contestadas
- Idempotente: limpia PRUEBA- previos antes de recrear
"""
import random
from django.core.management.base import BaseCommand
from django.db import transaction

from tenants.models import Tenant
from m00_onboarding.models import Trabajador

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
    help = 'Carga empleados de prueba (sin encuestas) en el tenant local (ID 1)'

    @transaction.atomic
    def handle(self, *args, **options):
        random.seed(SEED)

        try:
            tenant = Tenant.objects.get(id=1)
        except Tenant.DoesNotExist:
            self.stderr.write('Tenant ID 1 no encontrado. Ejecuta seed_dev primero.')
            return

        # Asegurar que el tenant tenga num_trabajadores correcto
        total = sum(c for _, _, c in AREAS)
        if tenant.num_trabajadores < total:
            tenant.num_trabajadores = total + 20
            tenant.save(update_fields=['num_trabajadores'])
            self.stdout.write(f'  num_trabajadores actualizado a {tenant.num_trabajadores}')

        # Limpiar empleados PRUEBA previos
        prev = Trabajador.objects.filter(
            tenant=tenant, num_empleado__startswith='PRUEBA-'
        ).count()
        Trabajador.objects.filter(
            tenant=tenant, num_empleado__startswith='PRUEBA-'
        ).delete()
        if prev:
            self.stdout.write(f'Eliminados {prev} empleados previos')

        # Generar empleados
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
            f'OK: {idx} empleados de prueba creados en tenant "{tenant.nombre}" (sin encuestas)'
        ))
        self.stdout.write('  Distribución por área:')
        for area, tipo_puesto, cantidad in AREAS:
            self.stdout.write(f'    {area:20s} / {tipo_puesto:15s}: {cantidad}')
