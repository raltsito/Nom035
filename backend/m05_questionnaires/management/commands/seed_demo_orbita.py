"""
Puebla datos demo realistas para el tenant Orbita (benja prueba).
Crea 20 trabajadores con perfiles variados, aplicaciones completadas y resultados.
Idempotente: borra y recrea los datos demo.
"""
import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction

from tenants.models import Tenant
from m00_onboarding.models import Trabajador, CicloNOM
from m05_questionnaires.models import (
    Cuestionario, Dominio, Pregunta,
    Aplicacion, RespuestaPregunta, GuiaLink,
)
from m06_results.models import ResultadoAplicacion, ResultadoDominio
from m06_results.scoring import calcular_resultado

# ---------------------------------------------------------------------------
# Perfil de cada trabajador
# (nombre, ap_paterno, area, tipo_puesto, tipo_contratacion, ats, risk_iii)
# ats  = True → requiere atención clínica Guía I
# risk = 0-4  → nivel de riesgo en Guía III (0=nulo … 4=muy_alto)
# ---------------------------------------------------------------------------
PERFILES = [
    ('Carlos',    'Mendoza',   'Produccion',     'Operativo',     'planta',    False, 0),
    ('Maria',     'Lopez',     'Produccion',     'Operativo',     'planta',    False, 1),
    ('Juan',      'Garcia',    'Produccion',     'Supervisor',    'planta',    False, 2),
    ('Ana',       'Martinez',  'Produccion',     'Operativo',     'planta',    True,  4),
    ('Pedro',     'Rodriguez', 'Produccion',     'Operativo',     'planta',    False, 3),
    ('Sofia',     'Hernandez', 'Produccion',     'Tecnico',       'planta',    False, 2),
    ('Luis',      'Gonzalez',  'Ventas',         'Operativo',     'planta',    False, 1),
    ('Laura',     'Perez',     'Ventas',         'Supervisor',    'planta',    True,  3),
    ('Diego',     'Sanchez',   'Ventas',         'Operativo',     'planta',    False, 4),
    ('Valeria',   'Ramirez',   'Ventas',         'Operativo',     'planta',    False, 2),
    ('Roberto',   'Torres',    'Administracion', 'Administrativo','planta',    False, 1),
    ('Carmen',    'Flores',    'Administracion', 'Gerente',       'planta',    False, 0),
    ('Miguel',    'Rivera',    'Administracion', 'Tecnico',       'planta',    False, 2),
    ('Patricia',  'Cruz',      'Administracion', 'Operativo',     'planta',    False, 3),
    ('Andres',    'Ortiz',     'TI',             'Tecnico',       'planta',    False, 1),
    ('Daniela',   'Vargas',    'TI',             'Tecnico',       'planta',    False, 0),
    ('Fernando',  'Jimenez',   'TI',             'Gerente',       'planta',    False, 2),
    ('Isabel',    'Reyes',     'RRHH',           'Supervisor',    'planta',    False, 2),
    ('Eduardo',   'Romero',    'RRHH',           'Operativo',     'planta',    False, 3),
    ('Gabriela',  'Morales',   'RRHH',           'Tecnico',       'planta',    False, 1),
]

RANDOM_SEED = 42


def _noise(spread=1):
    return random.choice([-spread, 0, 0, 0, spread])


def _valor_directo(risk):
    """Pregunta directa: más risk → más valor."""
    return max(0, min(4, risk + _noise()))


def _valor_inverso(risk):
    """Pregunta inversa: más risk → menos valor (score = 4 - valor)."""
    return max(0, min(4, (4 - risk) + _noise()))


def _respuestas_guia_iii(cuestionario, risk):
    """
    Genera dict {pregunta_id: valor} para Guía III según nivel de riesgo.
    """
    respuestas = {}
    tiene_clientes  = risk >= 2   # riesgo medio-alto → sección clientes aplica
    es_supervisor   = False        # se setea por fuera si el perfil aplica

    for dominio in cuestionario.dominios.prefetch_related('preguntas').all():
        preguntas = list(dominio.preguntas.all())

        # Preguntas filtro de D13/D14 (tipo si_no)
        filtro = next((p for p in preguntas if p.tipo_respuesta == 'si_no'), None)
        if filtro:
            if dominio.clave == 'D13':
                respuestas[filtro.id] = 1 if tiene_clientes else 0
                aplica = tiene_clientes
            elif dominio.clave == 'D14':
                respuestas[filtro.id] = 1 if es_supervisor else 0
                aplica = es_supervisor
            else:
                aplica = True

            if not aplica:
                continue

        for pregunta in preguntas:
            if pregunta.tipo_respuesta != 'frecuencia':
                continue
            if pregunta.inversa:
                respuestas[pregunta.id] = _valor_inverso(risk)
            else:
                respuestas[pregunta.id] = _valor_directo(risk)

    return respuestas


def _respuestas_guia_i(cuestionario, requiere_atencion):
    """
    Genera dict {pregunta_id: valor} para Guía I.
    Si requiere_atencion=True: D1 ≥1 Sí  Y  D2+D3+D4 ≥2 Sí.
    """
    respuestas = {}
    for dominio in cuestionario.dominios.prefetch_related('preguntas').all():
        preguntas = list(dominio.preguntas.all())
        if dominio.clave == 'D1':
            # Acontecimiento traumático
            for i, p in enumerate(preguntas):
                if requiere_atencion:
                    # Primer acontecimiento = Sí, resto = No
                    respuestas[p.id] = 1 if i == 0 else 0
                else:
                    respuestas[p.id] = 0
        else:
            # Secciones de síntomas (solo se muestran si D1 tuvo algún Sí)
            if not requiere_atencion:
                for p in preguntas:
                    respuestas[p.id] = 0
            else:
                # 2-4 síntomas positivos
                n_positivos = random.randint(2, min(4, len(preguntas)))
                indices_pos = set(random.sample(range(len(preguntas)), n_positivos))
                for i, p in enumerate(preguntas):
                    respuestas[p.id] = 1 if i in indices_pos else 0
    return respuestas


def _respuestas_guia_v(cuestionario, nombre, ap_paterno, area, tipo_puesto):
    """Rellena Guía V con datos del trabajador."""
    respuestas = {}
    for dominio in cuestionario.dominios.prefetch_related('preguntas').all():
        for pregunta in dominio.preguntas.all():
            t = pregunta.tipo_respuesta
            if t == 'texto':
                if 'Nombre' in pregunta.texto:
                    respuestas[pregunta.id] = f'{nombre} {ap_paterno}'
                elif 'Fecha' in pregunta.texto:
                    respuestas[pregunta.id] = '15/01/2026'
                elif 'Edad' in pregunta.texto:
                    respuestas[pregunta.id] = str(random.randint(22, 52))
                elif 'puesto' in pregunta.texto.lower() or 'profesion' in pregunta.texto.lower():
                    respuestas[pregunta.id] = tipo_puesto
                elif 'Departamento' in pregunta.texto or 'Area' in pregunta.texto:
                    respuestas[pregunta.id] = area
                elif 'experiencia' in pregunta.texto.lower():
                    respuestas[pregunta.id] = str(random.randint(1, 15))
                else:
                    respuestas[pregunta.id] = 'N/A'
            elif t == 'si_no':
                respuestas[pregunta.id] = random.choice([0, 1])
            elif t == 'opcion':
                opciones = pregunta.opciones
                if opciones:
                    respuestas[pregunta.id] = 0  # índice de opción
    return respuestas


class Command(BaseCommand):
    help = 'Puebla datos demo para tenant Orbita (benja prueba)'

    @transaction.atomic
    def handle(self, *args, **options):
        random.seed(RANDOM_SEED)

        # ── Tenant y ciclo ─────────────────────────────────────────────
        try:
            tenant = Tenant.objects.get(id=1)
        except Tenant.DoesNotExist:
            self.stderr.write('Tenant ID 1 no encontrado.')
            return

        # Asegurar num_trabajadores >= 50 para que aplique Guía III
        if tenant.num_trabajadores < 50:
            tenant.num_trabajadores = 100
            tenant.save(update_fields=['num_trabajadores'])
            self.stdout.write(f'  Actualizado num_trabajadores a 100')

        ciclo, _ = CicloNOM.objects.get_or_create(
            tenant=tenant,
            anio=2026,
            defaults={
                'estado': 'en_progreso',
                'fecha_inicio': '2026-01-01',
            },
        )
        self.stdout.write(f'Ciclo: {ciclo.anio} (ID {ciclo.id})')

        # ── Cuestionarios ──────────────────────────────────────────────
        try:
            guia_v   = Cuestionario.objects.get(clave='V')
            guia_i   = Cuestionario.objects.get(clave='I')
            guia_iii = Cuestionario.objects.get(clave='III')
        except Cuestionario.DoesNotExist as e:
            self.stderr.write(f'Cuestionario no encontrado: {e}. Ejecuta seed_cuestionarios primero.')
            return

        # ── GuiaLinks ──────────────────────────────────────────────────
        for cuest in [guia_v, guia_i, guia_iii]:
            GuiaLink.objects.get_or_create(
                tenant=tenant,
                ciclo=ciclo,
                cuestionario=cuest,
                defaults={'activo': True},
            )

        # ── Limpiar datos previos del demo ─────────────────────────────
        self.stdout.write('Limpiando datos demo previos...')
        Aplicacion.objects.filter(
            tenant=tenant, ciclo=ciclo,
            trabajador__num_empleado__startswith='DEMO-',
        ).delete()
        Trabajador.objects.filter(
            tenant=tenant,
            num_empleado__startswith='DEMO-',
        ).delete()

        # ── Crear trabajadores y aplicaciones ──────────────────────────
        self.stdout.write(f'Creando {len(PERFILES)} trabajadores...')
        total_calculados = 0

        for i, (nombre, ap_paterno, area, tipo_puesto, tipo_cont, ats, risk_iii) in enumerate(PERFILES):
            # 1) Trabajador
            trabajador = Trabajador.objects.create(
                tenant          = tenant,
                nombre          = nombre,
                apellido_paterno = ap_paterno,
                num_empleado    = f'DEMO-{i+1:03d}',
                area            = area,
                tipo_puesto     = tipo_puesto,
                tipo_contratacion = tipo_cont,
                activo          = True,
                tipo_jornada    = random.choice(['diurno', 'mixto', 'tiempo_completo']),
                sexo            = random.choice(['M', 'F']),
                edad            = random.randint(22, 55),
            )

            # 2) Aplicación + respuestas Guía V
            app_v = Aplicacion.objects.create(
                tenant=tenant, ciclo=ciclo,
                cuestionario=guia_v, trabajador=trabajador,
                estado='completado', fecha_completado=timezone.now(),
            )
            for pid, val in _respuestas_guia_v(guia_v, nombre, ap_paterno, area, tipo_puesto).items():
                RespuestaPregunta.objects.create(
                    tenant=tenant, aplicacion=app_v, pregunta_id=pid,
                    valor=val if isinstance(val, int) else None,
                    valor_texto=val if isinstance(val, str) else '',
                )

            # 3) Aplicación + respuestas Guía I
            app_i = Aplicacion.objects.create(
                tenant=tenant, ciclo=ciclo,
                cuestionario=guia_i, trabajador=trabajador,
                estado='completado', fecha_completado=timezone.now(),
            )
            for pid, val in _respuestas_guia_i(guia_i, ats).items():
                RespuestaPregunta.objects.create(
                    tenant=tenant, aplicacion=app_i, pregunta_id=pid, valor=val,
                )

            # 4) Aplicación + respuestas Guía III
            es_sup = tipo_puesto in ('Supervisor', 'Gerente')
            resp_iii = _respuestas_guia_iii(guia_iii, risk_iii)
            # Actualizar filtro supervisor según perfil
            for dominio in guia_iii.dominios.prefetch_related('preguntas').all():
                if dominio.clave == 'D14':
                    filtro = next((p for p in dominio.preguntas.all() if p.tipo_respuesta == 'si_no'), None)
                    if filtro:
                        resp_iii[filtro.id] = 1 if es_sup else 0

            app_iii = Aplicacion.objects.create(
                tenant=tenant, ciclo=ciclo,
                cuestionario=guia_iii, trabajador=trabajador,
                estado='completado', fecha_completado=timezone.now(),
            )
            for pid, val in resp_iii.items():
                RespuestaPregunta.objects.create(
                    tenant=tenant, aplicacion=app_iii, pregunta_id=pid, valor=val,
                )

            # 5) Calcular resultado para Guía I y III
            for app in [app_i, app_iii]:
                app.refresh_from_db()
                datos = calcular_resultado(app)
                if datos is None:
                    continue
                resultado, _ = ResultadoAplicacion.objects.update_or_create(
                    aplicacion=app,
                    defaults={
                        'puntaje_total':     datos['puntaje_total'],
                        'puntaje_max':       datos['puntaje_max'],
                        'categoria':         datos['categoria'],
                        'requiere_atencion': datos.get('requiere_atencion'),
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
                    ) for d in datos['dominios']
                ])
                total_calculados += 1

            self.stdout.write(
                f'  [{i+1:02d}] {nombre} {ap_paterno} — {area} / {tipo_puesto} '
                f'— Guia III: {"nulo bajo medio alto muy_alto".split()[risk_iii]}'
                f'{" [ATS]" if ats else ""}'
            )

        # ── Resumen final ──────────────────────────────────────────────
        self.stdout.write(self.style.SUCCESS(
            f'OK: {len(PERFILES)} trabajadores creados, {total_calculados} resultados calculados.'
        ))
        dist = {k: 0 for k in ['nulo', 'bajo', 'medio', 'alto', 'muy_alto']}
        for r, in zip([p[6] for p in PERFILES]):
            dist[['nulo', 'bajo', 'medio', 'alto', 'muy_alto'][r]] += 1
        self.stdout.write('  Distribución Guía III: ' + ', '.join(f'{k}={v}' for k, v in dist.items()))
        ats_total = sum(1 for p in PERFILES if p[5])
        self.stdout.write(f'  Casos ATS Guía I: {ats_total}')
