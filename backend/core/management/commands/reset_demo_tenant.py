from django.core.management.base import BaseCommand
from django.db import transaction

DEMO_TENANT_ID = 1  # pruebabenja


class Command(BaseCommand):
    help = 'Limpia todos los datos del tenant de prueba (id=1) sin borrar el tenant ni su admin.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirmar la operación sin prompt interactivo.',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            confirm = input(
                f'¿Borrar TODOS los datos del tenant demo (id={DEMO_TENANT_ID})? [s/N] '
            )
            if confirm.lower() != 's':
                self.stdout.write(self.style.WARNING('Operación cancelada.'))
                return

        tid = DEMO_TENANT_ID

        with transaction.atomic():
            totals = {}

            # Módulo 0 – Onboarding
            from m00_onboarding.models import Trabajador, CicloNOM
            totals['Trabajador'] = Trabajador.objects.filter(tenant_id=tid).delete()[0]
            totals['CicloNOM'] = CicloNOM.objects.filter(tenant_id=tid).delete()[0]

            # Módulo 1 – Comité
            from m01_committee.models import ComiteNOM, MiembroComite, CapacitacionDC3
            totals['MiembroComite'] = MiembroComite.objects.filter(tenant_id=tid).delete()[0]
            totals['ComiteNOM'] = ComiteNOM.objects.filter(tenant_id=tid).delete()[0]
            totals['CapacitacionDC3'] = CapacitacionDC3.objects.filter(tenant_id=tid).delete()[0]

            # Módulo 2 – Plan de acción
            from m02_action_plan.models import AccionMedida, PlanAccion
            totals['AccionMedida'] = AccionMedida.objects.filter(tenant_id=tid).delete()[0]
            totals['PlanAccion'] = PlanAccion.objects.filter(tenant_id=tid).delete()[0]

            # Módulo 3 – Política
            from m03_policy.models import PoliticaPrevension
            totals['PoliticaPrevension'] = PoliticaPrevension.objects.filter(tenant_id=tid).delete()[0]

            # Módulo 4 – Difusión
            from m04_dissemination.models import ActividadDifusion
            totals['ActividadDifusion'] = ActividadDifusion.objects.filter(tenant_id=tid).delete()[0]

            # Módulo 5 – Cuestionarios
            from m05_questionnaires.models import Aplicacion, AplicacionFoto, GuiaLink, RespuestaPregunta
            totals['RespuestaPregunta'] = RespuestaPregunta.objects.filter(tenant_id=tid).delete()[0]
            totals['AplicacionFoto'] = AplicacionFoto.objects.filter(tenant_id=tid).delete()[0]
            totals['Aplicacion'] = Aplicacion.objects.filter(tenant_id=tid).delete()[0]
            totals['GuiaLink'] = GuiaLink.objects.filter(tenant_id=tid).delete()[0]

            # Módulo 7 – Evidencias
            from m07_evidence.models import EvidenciaDocumento
            totals['EvidenciaDocumento'] = EvidenciaDocumento.objects.filter(tenant_id=tid).delete()[0]

            # Módulo 8 – Asistencia
            from m08_attendance.models import Asistente, Reunion
            totals['Asistente'] = Asistente.objects.filter(tenant_id=tid).delete()[0]
            totals['Reunion'] = Reunion.objects.filter(tenant_id=tid).delete()[0]

            # Usuarios empleados/auditores del tenant (conserva al admin pruebabenja)
            from accounts.models import User
            deleted_users = User.objects.filter(
                tenant_id=tid,
                rol__in=['empleado', 'auditor'],
            ).delete()[0]
            totals['User (empleados/auditores)'] = deleted_users

        grand_total = sum(totals.values())
        self.stdout.write(self.style.SUCCESS(f'\nTenant demo reseteado. {grand_total} registros eliminados:'))
        for model, count in totals.items():
            if count:
                self.stdout.write(f'  {model}: {count}')
