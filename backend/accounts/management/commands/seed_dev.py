from django.core.management.base import BaseCommand
from accounts.models import User
from tenants.models import Tenant


class Command(BaseCommand):
    help = 'Crea usuarios y empresa de prueba para desarrollo'

    def handle(self, *args, **options):
        # Super admin
        super_admin, created = User.objects.get_or_create(
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
            super_admin.set_password('Admin123!')
            super_admin.save()
            self.stdout.write(self.style.SUCCESS('Super admin creado'))
        else:
            self.stdout.write('Super admin ya existe')

        # Tenant de prueba
        tenant, created = Tenant.objects.get_or_create(
            rfc='XAXX010101000',
            defaults={
                'nombre': 'Empresa Demo SA de CV',
                'giro': 'Manufactura',
                'num_trabajadores': 50,
                'consultor': super_admin,
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Empresa demo creada'))
        else:
            self.stdout.write('Empresa demo ya existe')

        # Tenant admin
        tenant_admin, created = User.objects.get_or_create(
            email='admin@empresa.com',
            defaults={
                'username': 'tenantadmin',
                'first_name': 'Admin',
                'last_name': 'Empresa',
                'rol': User.TENANT_ADMIN,
                'tenant': tenant,
                'is_active': True,
            },
        )
        if created:
            tenant_admin.set_password('Admin123!')
            tenant_admin.save()
            self.stdout.write(self.style.SUCCESS('Tenant admin creado'))
        else:
            self.stdout.write('Tenant admin ya existe')

        self.stdout.write(self.style.SUCCESS('\n--- Credenciales ---'))
        self.stdout.write('Super Admin : superadmin@intra.com / Admin123!')
        self.stdout.write('Tenant Admin: admin@empresa.com   / Admin123!')
