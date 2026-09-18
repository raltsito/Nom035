"""
Importa el Programa de intervencion NOM-035 (OIL) y el Plan de comunicacion
del tenant NEAPCO desde los Excel entregados por el cliente, hacia:

  - m00_onboarding.CicloNOM  (se crea si no existe)
  - m02_action_plan.PlanAccion / AccionMedida   <- "2.1 OIL.xlsx"
  - m04_dissemination.ActividadDifusion         <- "2.2 Plan de comunicacion.xlsx"

"2.3 Programa de control y mitigacion.xlsx" es una plantilla sin filas de
datos (solo encabezados y nombres de factores de riesgo) al momento de
escribir este comando: no se importa nada de ahi.

Por defecto corre en modo simulacro (no escribe nada). Usar --apply para
persistir los cambios. Es idempotente: si una accion/actividad con la misma
descripcion + fecha ya existe para el tenant, se omite en vez de duplicarse.

Uso:
    python manage.py importar_neapco_intervencion
    python manage.py importar_neapco_intervencion --apply
"""
import datetime
import re

import openpyxl
from django.core.management.base import BaseCommand
from django.db import transaction

from tenants.models import Tenant
from m00_onboarding.models import CicloNOM
from m02_action_plan.models import PlanAccion, AccionMedida
from m04_dissemination.models import ActividadDifusion

TENANT_RFC = 'NEA010101AA1'

OIL_PATH = r'C:\Users\carlo\Downloads\2.1 OIL.xlsx'
COMUNICACION_PATH = r'C:\Users\carlo\Downloads\2.2 Plan de comunicación.xlsx'

CICLO_ANIO = 2025
CICLO_FECHA_INICIO = datetime.date(2025, 7, 9)

FORMATO_A_TIPO_DIFUSION = {
    'sensibilizacion': 'platica',
    'triptico': 'cartel',
    'video': 'otro',
    'encuesta / foro': 'otro',
}


def _norm(value):
    if value is None:
        return ''
    text = str(value).strip().lower()
    text = text.replace('í', 'i').replace('ó', 'o').replace('á', 'a').replace('é', 'e').replace('ú', 'u')
    return text


def _to_date(value):
    if value is None or value == '':
        return None
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    return None


def _clean_text(value):
    if value is None:
        return ''
    return re.sub(r'\s+', ' ', str(value).replace('\xa0', ' ')).strip()


class Command(BaseCommand):
    help = 'Importa el programa de intervencion (OIL) y el plan de comunicacion de NEAPCO'

    def add_arguments(self, parser):
        parser.add_argument('--apply', action='store_true', help='Persistir los cambios (por defecto es simulacro).')
        parser.add_argument('--oil-path', default=OIL_PATH)
        parser.add_argument('--comunicacion-path', default=COMUNICACION_PATH)

    def handle(self, *args, **options):
        apply_changes = options['apply']

        try:
            tenant = Tenant.objects.get(rfc=TENANT_RFC)
        except Tenant.DoesNotExist:
            self.stderr.write(self.style.ERROR(f'Tenant con RFC "{TENANT_RFC}" no encontrado.'))
            return

        self.stdout.write(f'Tenant: "{tenant.nombre}" (ID {tenant.id})')
        self.stdout.write(self.style.WARNING('MODO SIMULACRO (usa --apply para persistir)') if not apply_changes
                           else self.style.SUCCESS('MODO APLICAR: se van a escribir cambios en la base de datos'))

        acciones = self._parse_oil(options['oil_path'])
        actividades = self._parse_comunicacion(options['comunicacion_path'])

        self.stdout.write(f'\nOIL.xlsx -> {len(acciones)} acciones/medidas detectadas')
        self.stdout.write(f'Plan de comunicacion.xlsx -> {len(actividades)} actividades de difusion detectadas')

        with transaction.atomic():
            ciclo, ciclo_creado = CicloNOM.objects.get_or_create(
                tenant=tenant,
                anio=CICLO_ANIO,
                defaults=dict(
                    estado='en_progreso',
                    fecha_inicio=CICLO_FECHA_INICIO,
                    notas='Ciclo creado a partir de la documentacion historica '
                          '(OIL, Plan de comunicacion) entregada por el cliente.',
                ),
            )
            self.stdout.write(('Creado' if ciclo_creado else 'Ya existia') + f' CicloNOM {ciclo.anio} (id={ciclo.id})')

            plan, plan_creado = PlanAccion.objects.get_or_create(
                tenant=tenant,
                ciclo=ciclo,
                defaults=dict(descripcion='Programa de intervencion NOM-035-STPS-2018 (OIL)'),
            )
            self.stdout.write(('Creado' if plan_creado else 'Ya existia') + f' PlanAccion (id={plan.id})')

            existentes_accion = set(
                AccionMedida.objects.filter(plan=plan)
                .values_list('descripcion', 'fecha_limite')
            )
            nuevas_acciones = 0
            for a in acciones:
                key = (a['descripcion'], a['fecha_limite'])
                if key in existentes_accion:
                    continue
                nuevas_acciones += 1
                if apply_changes:
                    AccionMedida.objects.create(tenant=tenant, plan=plan, **a)
            self.stdout.write(f'AccionMedida: {nuevas_acciones} nuevas (de {len(acciones)} filas), '
                               f'{len(acciones) - nuevas_acciones} ya existian')

            existentes_difusion = set(
                ActividadDifusion.objects.filter(tenant=tenant, ciclo=ciclo)
                .values_list('titulo', 'fecha')
            )
            nuevas_actividades = 0
            for act in actividades:
                key = (act['titulo'], act['fecha'])
                if key in existentes_difusion:
                    continue
                nuevas_actividades += 1
                if apply_changes:
                    ActividadDifusion.objects.create(tenant=tenant, ciclo=ciclo, **act)
            self.stdout.write(f'ActividadDifusion: {nuevas_actividades} nuevas (de {len(actividades)} filas), '
                               f'{len(actividades) - nuevas_actividades} ya existian')

            if not apply_changes:
                transaction.set_rollback(True)

        if apply_changes:
            self.stdout.write(self.style.SUCCESS('\nOK: cambios aplicados.'))
        else:
            self.stdout.write(self.style.WARNING('\nSimulacro completo, nada se escribio. Corre con --apply.'))

    # ------------------------------------------------------------------
    def _parse_oil(self, path):
        wb = openpyxl.load_workbook(path, data_only=True)
        ws = wb['OIL']
        acciones = []
        section = 'I.- SENSIBILIZACION Y CONCIENTIZACION'
        sub_label = ''

        for row in ws.iter_rows(min_row=8, max_row=ws.max_row, values_only=True):
            no, fecha_inicio, problema, actividad, depto, nombre, fecha_compromiso, status = row[:8]

            is_header = (
                no not in (None, '')
                and not str(no).strip().isdigit()
                and all(v in (None, '') for v in row[1:8])
            )
            if is_header:
                section = _clean_text(no)
                sub_label = ''
                continue

            if no in (None, '') or not str(no).strip().isdigit():
                continue

            descripcion = _clean_text(actividad)
            if not descripcion:
                continue

            if _clean_text(problema):
                sub_label = _clean_text(problema)

            fecha_limite = _to_date(fecha_compromiso)
            if fecha_limite is None:
                # AccionMedida.fecha_limite es NOT NULL: sin fecha compromiso no se puede
                # crear un registro valido, se omite y se reporta.
                self.stdout.write(self.style.WARNING(
                    f'  omitida (sin fecha compromiso): {descripcion[:80]}'
                ))
                continue

            status_val = _clean_text(status)
            completado = status_val == '100'

            factor_riesgo = f'{section} — {sub_label}' if sub_label else section
            notas = []
            fi = _to_date(fecha_inicio)
            if fi:
                notas.append(f'Fecha de inicio original: {fi.isoformat()}')
            if _clean_text(depto):
                notas.append(f'Departamento: {_clean_text(depto)}')

            acciones.append(dict(
                descripcion=descripcion,
                factor_riesgo=factor_riesgo[:300],
                responsable=_clean_text(nombre)[:200],
                fecha_limite=fecha_limite,
                estado='completado' if completado else 'pendiente',
                fecha_completado=fecha_limite if completado else None,
                avance_notas='. '.join(notas),
            ))

        wb.close()
        return acciones

    def _parse_comunicacion(self, path):
        wb = openpyxl.load_workbook(path, data_only=True)
        ws = wb.worksheets[0]
        actividades = []

        for row in ws.iter_rows(min_row=3, max_row=ws.max_row, values_only=True):
            no, punto, contenido, formato, duracion, medio, f_inicio, f_compromiso, f_termino = row[:9]
            if no in (None, ''):
                continue

            titulo = _clean_text(punto)
            if not titulo:
                continue

            fecha = _to_date(f_compromiso) or _to_date(f_inicio) or _to_date(f_termino)
            if fecha is None:
                self.stdout.write(self.style.WARNING(f'  omitida (sin fecha): {titulo}'))
                continue

            partes_desc = []
            if _clean_text(contenido):
                partes_desc.append(_clean_text(contenido))
            detalle = []
            if _clean_text(formato):
                detalle.append(f'Formato: {_clean_text(formato)}')
            if _clean_text(duracion):
                detalle.append(f'Duracion: {_clean_text(duracion)}')
            if _clean_text(medio):
                detalle.append(f'Medio: {_clean_text(medio)}')
            if detalle:
                partes_desc.append(' / '.join(detalle))

            tipo = FORMATO_A_TIPO_DIFUSION.get(_norm(formato), 'otro')

            actividades.append(dict(
                tipo=tipo,
                titulo=titulo[:300],
                descripcion='. '.join(partes_desc),
                fecha=fecha,
                num_participantes=0,
                responsable='',
            ))

        wb.close()
        return actividades
