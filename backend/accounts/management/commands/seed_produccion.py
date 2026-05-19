"""
Crea el super_admin ORBITA y los 15 tenants con sus tenant_admin.
Idempotente: puede ejecutarse varias veces sin duplicar registros.

Uso:
    python manage.py seed_produccion
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import User
from tenants.models import Tenant

# ---------------------------------------------------------------------------
# Super admin
# ---------------------------------------------------------------------------

SUPER_ADMIN = {
    'username':   'ORBITA',
    'email':      'superadmin@orbita.com',
    'first_name': 'Orbita',
    'last_name':  'Admin',
    'password':   '@Orb!t4_Mx25',
}

# ---------------------------------------------------------------------------
# Tenants + sus admins
# RFC y num_trabajadores son placeholders — actualizar en la app o BD.
# ---------------------------------------------------------------------------

TENANTS = [
    {
        'tenant': {
            'nombre':           'Piedras Negras I & II',
            'rfc':              'PNI010101AA1',
            'giro':             'Manufactura',
            'num_trabajadores': 100,
        },
        'admin': {
            'username':   'pnegras12',
            'email':      'admin.pnegras12@cliente.com',
            'first_name': 'Admin',
            'last_name':  'Piedras Negras I II',
            'password':   'PN12#Co4h_25!',
        },
    },
    {
        'tenant': {
            'nombre':           'Piedras Negras III',
            'rfc':              'PN3010101AA3',
            'giro':             'Manufactura',
            'num_trabajadores': 100,
        },
        'admin': {
            'username':   'pnegras3',
            'email':      'admin.pnegras3@cliente.com',
            'first_name': 'Admin',
            'last_name':  'Piedras Negras III',
            'password':   'PN3$C0ah_25!',
        },
    },
    {
        'tenant': {
            'nombre':           'Piedras Negras IV',
            'rfc':              'PN4010101AA4',
            'giro':             'Manufactura',
            'num_trabajadores': 100,
        },
        'admin': {
            'username':   'pnegras4',
            'email':      'admin.pnegras4@cliente.com',
            'first_name': 'Admin',
            'last_name':  'Piedras Negras IV',
            'password':   'PN4&C04h_25!',
        },
    },
    {
        'tenant': {
            'nombre':           'San Luis',
            'rfc':              'SLU010101AA1',
            'giro':             'Manufactura',
            'num_trabajadores': 100,
        },
        'admin': {
            'username':   'sanluis',
            'email':      'admin.sanluis@cliente.com',
            'first_name': 'Admin',
            'last_name':  'San Luis',
            'password':   'SL#P0t0s1_25!',
        },
    },
    {
        'tenant': {
            'nombre':           'Puebla',
            'rfc':              'PUE010101AA1',
            'giro':             'Manufactura',
            'num_trabajadores': 100,
        },
        'admin': {
            'username':   'puebla',
            'email':      'admin.puebla@cliente.com',
            'first_name': 'Admin',
            'last_name':  'Puebla',
            'password':   'Pu3@M3x_25!',
        },
    },
    {
        'tenant': {
            'nombre':           'Hermosillo',
            'rfc':              'HER010101AA1',
            'giro':             'Manufactura',
            'num_trabajadores': 100,
        },
        'admin': {
            'username':   'hermosillo',
            'email':      'admin.hermosillo@cliente.com',
            'first_name': 'Admin',
            'last_name':  'Hermosillo',
            'password':   'H3r#S0n0r4_25!',
        },
    },
    {
        'tenant': {
            'nombre':           'Planta 726 Ramos',
            'rfc':              'RAM010101AA1',
            'giro':             'Manufactura',
            'num_trabajadores': 100,
        },
        'admin': {
            'username':   'ramos726',
            'email':      'admin.ramos726@cliente.com',
            'first_name': 'Admin',
            'last_name':  'Ramos 726',
            'password':   'R726$NL_25!x',
        },
    },
    {
        'tenant': {
            'nombre':           'Naucalpan',
            'rfc':              'NAU010101AA1',
            'giro':             'Manufactura',
            'num_trabajadores': 100,
        },
        'admin': {
            'username':   'naucalpan',
            'email':      'admin.naucalpan@cliente.com',
            'first_name': 'Admin',
            'last_name':  'Naucalpan',
            'password':   'N4u@EdoMx_25!',
        },
    },
    {
        'tenant': {
            'nombre':           'Reynosa',
            'rfc':              'REY010101AA1',
            'giro':             'Manufactura',
            'num_trabajadores': 100,
        },
        'admin': {
            'username':   'reynosa',
            'email':      'admin.reynosa@cliente.com',
            'first_name': 'Admin',
            'last_name':  'Reynosa',
            'password':   'R3y#T4mp_25!',
        },
    },
    {
        'tenant': {
            'nombre':           'Silao',
            'rfc':              'SIL010101AA1',
            'giro':             'Manufactura',
            'num_trabajadores': 100,
        },
        'admin': {
            'username':   'silao',
            'email':      'admin.silao@cliente.com',
            'first_name': 'Admin',
            'last_name':  'Silao',
            'password':   'S!l4o@Gt0_25!',
        },
    },
    {
        'tenant': {
            'nombre':           'Toluca',
            'rfc':              'TOL010101AA1',
            'giro':             'Manufactura',
            'num_trabajadores': 100,
        },
        'admin': {
            'username':   'toluca',
            'email':      'admin.toluca@cliente.com',
            'first_name': 'Admin',
            'last_name':  'Toluca',
            'password':   'T0l#EdoMx_25!',
        },
    },
    {
        'tenant': {
            'nombre':           'Saltillo',
            'rfc':              'SAL010101AA1',
            'giro':             'Manufactura',
            'num_trabajadores': 100,
        },
        'admin': {
            'username':   'saltillo',
            'email':      'admin.saltillo@cliente.com',
            'first_name': 'Admin',
            'last_name':  'Saltillo',
            'password':   'S4lt@C04h_25!',
        },
    },
    {
        'tenant': {
            'nombre':           'Zapotitlan',
            'rfc':              'ZAP010101AA1',
            'giro':             'Manufactura',
            'num_trabajadores': 100,
        },
        'admin': {
            'username':   'zapotitlan',
            'email':      'admin.zapotitlan@cliente.com',
            'first_name': 'Admin',
            'last_name':  'Zapotitlan',
            'password':   'Z4p0@CDMX_25!',
        },
    },
    {
        'tenant': {
            'nombre':           'Arteaga',
            'rfc':              'ART010101AA1',
            'giro':             'Manufactura',
            'num_trabajadores': 100,
        },
        'admin': {
            'username':   'arteaga',
            'email':      'admin.arteaga@cliente.com',
            'first_name': 'Admin',
            'last_name':  'Arteaga',
            'password':   'Art3@C04h_25!',
        },
    },
    {
        'tenant': {
            'nombre':           'PRUEBA',
            'rfc':              'PRU010101AA1',
            'giro':             'Pruebas',
            'num_trabajadores': 10,
        },
        'admin': {
            'username':   'prueba',
            'email':      'admin.prueba@cliente.com',
            'first_name': 'Admin',
            'last_name':  'Prueba',
            'password':   'Pr3#T3st_25!x',
        },
    },
]


class Command(BaseCommand):
    help = 'Crea el super_admin ORBITA y los 15 tenants de produccion con sus admins'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset-passwords',
            action='store_true',
            help='Sobreescribe las contrasenas de usuarios ya existentes',
        )

    def handle(self, *args, **options):
        reset = options['reset_passwords']
        with transaction.atomic():
            orbita = self._ensure_super_admin(reset)
            for entry in TENANTS:
                tenant = self._ensure_tenant(entry['tenant'], orbita)
                self._ensure_admin(entry['admin'], tenant, reset)

        self._print_summary()

    def _ensure_super_admin(self, reset=False):
        user, created = User.objects.get_or_create(
            username=SUPER_ADMIN['username'],
            defaults={
                'email':      SUPER_ADMIN['email'],
                'first_name': SUPER_ADMIN['first_name'],
                'last_name':  SUPER_ADMIN['last_name'],
                'rol':        User.SUPER_ADMIN,
                'is_active':  True,
                'is_staff':   True,
            },
        )
        if created or reset:
            user.set_password(SUPER_ADMIN['password'])
            user.save()
            self._ok(f'Super admin "{user.username}" {"creado" if created else "password actualizado"}')
        else:
            self._skip(f'Super admin "{user.username}" ya existe')
        return user

    def _ensure_tenant(self, data, consultor):
        tenant, created = Tenant.objects.get_or_create(
            rfc=data['rfc'],
            defaults={
                'nombre':           data['nombre'],
                'giro':             data['giro'],
                'num_trabajadores': data['num_trabajadores'],
                'consultor':        consultor,
            },
        )
        if created:
            self._ok(f'  Tenant "{tenant.nombre}" creado')
        else:
            self._skip(f'  Tenant "{tenant.nombre}" ya existe')
        return tenant

    def _ensure_admin(self, data, tenant, reset=False):
        user, created = User.objects.get_or_create(
            username=data['username'],
            defaults={
                'email':      data['email'],
                'first_name': data['first_name'],
                'last_name':  data['last_name'],
                'rol':        User.TENANT_ADMIN,
                'tenant':     tenant,
                'is_active':  True,
            },
        )
        if created or reset:
            user.set_password(data['password'])
            user.save()
            self._ok(f'    Admin "{user.username}" {"creado" if created else "password actualizado"}')
        else:
            self._skip(f'    Admin "{user.username}" ya existe')
        return user

    def _ok(self, msg):
        self.stdout.write(self.style.SUCCESS(f'[OK] {msg}'))

    def _skip(self, msg):
        self.stdout.write(self.style.WARNING(f'[--] {msg}'))

    def _print_summary(self):
        sep = '-' * 55
        self.stdout.write('\n' + sep)
        self.stdout.write(self.style.SUCCESS('PRODUCCION LISTA'))
        self.stdout.write(sep)
        self.stdout.write(f'  Super admin : {SUPER_ADMIN["username"]}')
        self.stdout.write(f'  Password    : {SUPER_ADMIN["password"]}')
        self.stdout.write('')
        self.stdout.write('  Tenants y admins:')
        for e in TENANTS:
            self.stdout.write(
                f'    {e["tenant"]["nombre"]:<28} {e["admin"]["username"]:<14} {e["admin"]["password"]}'
            )
        self.stdout.write('')
        self.stdout.write(sep)
        self.stdout.write('  NOTA: RFC y num_trabajadores son placeholders.')
        self.stdout.write('        Actualizar en la app despues de ejecutar.')
        self.stdout.write(sep)
