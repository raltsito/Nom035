"""Carga el export anonimizado de la planta PRUEBA
(`export_planta_prueba_ciclo2026.json`) para la prueba integral del flujo
dinámico del Informe Diagnóstico.

EXCLUSIVO de desarrollo/pruebas:
- Se niega a ejecutarse si `settings.DEBUG` es False, salvo que se defina
  NOM035_PERMITIR_FIXTURE=1 (p. ej. dentro del runner de tests en CI).
- No toca ningún tenant existente: crea (o reutiliza) el tenant PRUEBA con
  un RFC sintético reservado.

Los resultados NO se insertan desde el JSON: se cargan trabajadores,
aplicaciones y respuestas, y después se ejecuta el MISMO motor de cálculo
que producción (m06_results.services.calcular_ciclo). Así el informe de
prueba atraviesa exactamente el flujo real.
"""
import json
import os
from datetime import date
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.dateparse import parse_datetime

RFC_PRUEBA = 'PRU010101PRB'

RUTA_FIXTURE_DEFAULT = (
    Path(__file__).resolve().parents[2] / 'tests_fixtures'
    / 'export_planta_prueba_ciclo2026.json'
)

_CAMPOS_TRABAJADOR = (
    'sexo', 'edad', 'estado_civil', 'nivel_estudios', 'tipo_puesto', 'area',
    'tipo_contratacion', 'tipo_personal', 'tipo_jornada', 'rotacion_turnos',
    'tiempo_puesto_actual', 'experiencia_anios', 'experiencia_empresa_anios',
    'activo',
)


class Command(BaseCommand):
    help = 'Carga el fixture anonimizado de la planta PRUEBA (solo dev/tests).'

    def add_arguments(self, parser):
        parser.add_argument('--ruta', default=str(RUTA_FIXTURE_DEFAULT),
                            help='Ruta del JSON exportado.')

    @transaction.atomic
    def handle(self, *args, **opts):
        if not settings.DEBUG and os.environ.get('NOM035_PERMITIR_FIXTURE') != '1':
            raise CommandError(
                'cargar_fixture_prueba es exclusivo de desarrollo/pruebas '
                '(DEBUG=False y NOM035_PERMITIR_FIXTURE sin definir).'
            )

        ruta = Path(opts['ruta'])
        if not ruta.exists():
            raise CommandError(f'No existe el fixture: {ruta}')
        data = json.loads(ruta.read_text(encoding='utf-8'))

        from accounts.models import User
        from m00_onboarding.models import CicloNOM, Trabajador
        from m05_questionnaires.models import (
            Aplicacion, Cuestionario, Pregunta, RespuestaPregunta,
        )
        from m06_results.services import calcular_ciclo
        from tenants.models import Tenant

        # Catálogo oficial de cuestionarios/preguntas (idempotente).
        if not Cuestionario.objects.filter(clave__in=('I', 'III', 'V')).count() == 3:
            call_command('seed_cuestionarios')

        consultor = User.objects.filter(rol='super_admin').first()
        if consultor is None:
            consultor = User.objects.create(
                username='consultor_prueba', email='consultor_prueba@example.com',
                first_name='Consultor', last_name='Prueba', rol='super_admin',
            )
            consultor.set_unusable_password()
            consultor.save()

        t = data['tenant']
        tenant, _ = Tenant.objects.update_or_create(
            rfc=RFC_PRUEBA,
            defaults={
                'nombre':           t['nombre'],
                'razon_social':     t.get('razon_social', ''),
                'giro':             t.get('giro', ''),
                'num_trabajadores': t.get('num_trabajadores', 0),
                'direccion':        t.get('direccion', ''),
                'consultor':        consultor,
            },
        )

        anio = data['ciclo']['anio']
        ciclo, _ = CicloNOM.objects.get_or_create(
            tenant=tenant, anio=anio,
            defaults={'fecha_inicio': date(anio, 1, 1), 'estado': 'iniciado'},
        )

        # Limpieza idempotente del ciclo PRUEBA (solo este tenant sintético).
        Aplicacion.objects.filter(tenant=tenant, ciclo=ciclo).delete()
        Trabajador.objects.filter(tenant=tenant).delete()

        trabajadores = {}
        for tr in data['trabajadores']:
            campos = {c: tr.get(c) for c in _CAMPOS_TRABAJADOR}
            campos = {c: ('' if v is None and c not in (
                'edad', 'rotacion_turnos', 'tiempo_puesto_actual',
                'experiencia_anios', 'experiencia_empresa_anios', 'activo') else v)
                for c, v in campos.items()}
            trabajadores[tr['trabajador_id']] = Trabajador.objects.create(
                tenant=tenant,
                nombre=tr['folio'],
                apellido_paterno='',
                num_empleado=tr['folio'],
                **campos,
            )

        cuestionarios = {c.clave: c for c in Cuestionario.objects.all()}
        aplicaciones = {}
        for ap in data['aplicaciones']:
            aplicaciones[ap['aplicacion_id']] = Aplicacion.objects.create(
                tenant=tenant,
                ciclo=ciclo,
                cuestionario=cuestionarios[ap['cuestionario_clave']],
                trabajador=trabajadores[ap['trabajador_id']],
                estado=ap['estado'],
                fecha_completado=parse_datetime(ap['fecha_completado'])
                if ap.get('fecha_completado') else None,
            )

        # pregunta_id del export → Pregunta local por (guía, dominio, orden).
        preguntas_local = {
            (p.dominio.cuestionario.clave, p.dominio.clave, p.orden): p
            for p in Pregunta.objects.select_related('dominio__cuestionario')
        }
        mapa_pregunta = {}
        for cp in data['catalogo_preguntas']:
            clave = (cp['cuestionario_clave'], cp['dominio_clave'], cp['orden'])
            local = preguntas_local.get(clave)
            if local is None:
                raise CommandError(f'Pregunta del export sin equivalente local: {clave}')
            mapa_pregunta[cp['pregunta_id']] = local

        RespuestaPregunta.objects.bulk_create([
            RespuestaPregunta(
                tenant=tenant,
                aplicacion=aplicaciones[r['aplicacion_id']],
                pregunta=mapa_pregunta[r['pregunta_id']],
                valor=r['valor'],
                valor_texto=r.get('valor_texto') or '',
            )
            for r in data['respuestas']
            if r['aplicacion_id'] in aplicaciones
        ])

        # Mismo motor que producción (POST /resultados/calcular/).
        resumen = calcular_ciclo(tenant, ciclo)
        if resumen is None:
            raise CommandError('El fixture no dejó aplicaciones completadas.')

        self.stdout.write(self.style.SUCCESS(
            f"Fixture PRUEBA cargado: tenant={tenant.id} ciclo={ciclo.id} "
            f"trabajadores={len(trabajadores)} aplicaciones={len(aplicaciones)} "
            f"resultados={resumen['total']} (motor {resumen['version_motor']})"
        ))
        return str(ciclo.id)
