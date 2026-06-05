"""
Puebla el tenant pruebabenja con 110 empleados de prueba.
Todos tienen "PRUEBA" en el nombre. Distribución realista para capturas del manual.
Idempotente: limpia trabajadores PRUEBA- previos antes de recrear.
"""
import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction

from tenants.models import Tenant
from m00_onboarding.models import Trabajador, CicloNOM
from m05_questionnaires.models import (
    Cuestionario, Aplicacion, RespuestaPregunta, GuiaLink,
)
from m06_results.models import ResultadoAplicacion, ResultadoDominio
from m06_results.scoring import calcular_resultado

SEED = 7

# ── Catálogos ────────────────────────────────────────────────────────────────
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

# (area, tipo_puesto, proporcion, riesgo_base, prob_ats)
AREAS = [
    ('Produccion',      'Operativo',     20, 3, 0.10),
    ('Produccion',      'Tecnico',        8, 2, 0.05),
    ('Produccion',      'Supervisor',     4, 2, 0.05),
    ('Ventas',          'Operativo',     15, 2, 0.08),
    ('Ventas',          'Supervisor',     4, 1, 0.05),
    ('Ventas',          'Gerente',        2, 1, 0.00),
    ('Administracion',  'Administrativo',10, 1, 0.05),
    ('Administracion',  'Gerente',        2, 0, 0.00),
    ('TI',              'Tecnico',        8, 1, 0.05),
    ('TI',              'Gerente',        2, 1, 0.00),
    ('RRHH',            'Administrativo', 6, 2, 0.10),
    ('RRHH',            'Supervisor',     3, 1, 0.05),
    ('Operaciones',     'Operativo',     12, 3, 0.12),
    ('Operaciones',     'Supervisor',     4, 2, 0.05),
    ('Logistica',       'Operativo',      6, 4, 0.15),
    ('Calidad',         'Tecnico',        4, 2, 0.05),
]


def _noise(spread=1):
    return random.choice([-spread, 0, 0, 0, spread])


def _valor_directo(risk):
    return max(0, min(4, risk + _noise()))


def _valor_inverso(risk):
    return max(0, min(4, (4 - risk) + _noise()))


def _respuestas_guia_iii(cuestionario, risk, es_sup):
    tiene_clientes = risk >= 2
    respuestas = {}
    for dominio in cuestionario.dominios.prefetch_related('preguntas').all():
        preguntas = list(dominio.preguntas.all())
        filtro = next((p for p in preguntas if p.tipo_respuesta == 'si_no'), None)
        if filtro:
            if dominio.clave == 'D13':
                respuestas[filtro.id] = 1 if tiene_clientes else 0
                if not tiene_clientes:
                    continue
            elif dominio.clave == 'D14':
                respuestas[filtro.id] = 1 if es_sup else 0
                if not es_sup:
                    continue
        for p in preguntas:
            if p.tipo_respuesta != 'frecuencia':
                continue
            respuestas[p.id] = _valor_inverso(risk) if p.inversa else _valor_directo(risk)
    return respuestas


def _respuestas_guia_i(cuestionario, requiere_atencion):
    respuestas = {}
    for dominio in cuestionario.dominios.prefetch_related('preguntas').all():
        preguntas = list(dominio.preguntas.all())
        if dominio.clave == 'D1':
            for i, p in enumerate(preguntas):
                respuestas[p.id] = 1 if (requiere_atencion and i == 0) else 0
        else:
            if not requiere_atencion:
                for p in preguntas:
                    respuestas[p.id] = 0
            else:
                n_pos = random.randint(2, min(4, len(preguntas)))
                idx_pos = set(random.sample(range(len(preguntas)), n_pos))
                for i, p in enumerate(preguntas):
                    respuestas[p.id] = 1 if i in idx_pos else 0
    return respuestas


def _respuestas_guia_v(cuestionario, nombre_completo, area, tipo_puesto):
    respuestas = {}
    for dominio in cuestionario.dominios.prefetch_related('preguntas').all():
        for p in dominio.preguntas.all():
            t = p.tipo_respuesta
            if t == 'texto':
                texto_lower = p.texto.lower()
                if 'nombre' in texto_lower:
                    respuestas[p.id] = nombre_completo
                elif 'fecha' in texto_lower:
                    respuestas[p.id] = '15/01/2026'
                elif 'edad' in texto_lower:
                    respuestas[p.id] = str(random.randint(22, 55))
                elif 'puesto' in texto_lower or 'profesion' in texto_lower:
                    respuestas[p.id] = tipo_puesto
                elif 'departamento' in texto_lower or 'area' in texto_lower:
                    respuestas[p.id] = area
                elif 'experiencia' in texto_lower or 'antiguedad' in texto_lower:
                    respuestas[p.id] = str(random.randint(1, 15))
                else:
                    respuestas[p.id] = 'N/A'
            elif t == 'si_no':
                respuestas[p.id] = random.choice([0, 1])
            elif t == 'opcion':
                respuestas[p.id] = 0
    return respuestas


def _calcular_y_guardar(app, datos):
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
    return resultado


class Command(BaseCommand):
    help = 'Crea 110 empleados PRUEBA en tenant pruebabenja con resultados calculados'

    @transaction.atomic
    def handle(self, *args, **options):
        random.seed(SEED)

        # ── Tenant ──────────────────────────────────────────────────────
        try:
            tenant = Tenant.objects.get(id=1)
        except Tenant.DoesNotExist:
            self.stderr.write('Tenant ID 1 no encontrado.')
            return

        if tenant.num_trabajadores < 110:
            tenant.num_trabajadores = 150
            tenant.save(update_fields=['num_trabajadores'])

        # ── Ciclo 2026 ──────────────────────────────────────────────────
        ciclo, creado = CicloNOM.objects.get_or_create(
            tenant=tenant, anio=2026,
            defaults={'estado': 'en_progreso', 'fecha_inicio': '2026-01-01'},
        )
        self.stdout.write(f'Ciclo 2026 (ID {ciclo.id}) {"creado" if creado else "existente"}')

        # ── Cuestionarios ───────────────────────────────────────────────
        try:
            guia_v   = Cuestionario.objects.get(clave='V')
            guia_i   = Cuestionario.objects.get(clave='I')
            guia_iii = Cuestionario.objects.get(clave='III')
        except Cuestionario.DoesNotExist as e:
            self.stderr.write(f'Falta cuestionario: {e}')
            return

        for cuest in [guia_v, guia_i, guia_iii]:
            GuiaLink.objects.get_or_create(
                tenant=tenant, ciclo=ciclo, cuestionario=cuest,
                defaults={'activo': True},
            )

        # ── Limpiar datos previos PRUEBA ─────────────────────────────────
        self.stdout.write('Limpiando empleados PRUEBA previos...')
        prev = Trabajador.objects.filter(
            tenant=tenant, num_empleado__startswith='PRUEBA-'
        ).count()
        Aplicacion.objects.filter(
            tenant=tenant, ciclo=ciclo,
            trabajador__num_empleado__startswith='PRUEBA-',
        ).delete()
        Trabajador.objects.filter(
            tenant=tenant, num_empleado__startswith='PRUEBA-'
        ).delete()
        if prev:
            self.stdout.write(f'  Eliminados {prev} empleados previos')

        # ── Generar perfiles ─────────────────────────────────────────────
        perfiles = []
        idx = 0
        nombres_usados = set()

        for area, tipo_puesto, cantidad, riesgo_base, prob_ats in AREAS:
            for _ in range(cantidad):
                # Nombre único
                while True:
                    nombre = random.choice(NOMBRES)
                    ap     = random.choice(AP_PATERNO)
                    clave  = f'{nombre}{ap}'
                    if clave not in nombres_usados:
                        nombres_usados.add(clave)
                        break

                # Riesgo con variación ±1 para distribución natural
                risk = max(0, min(4, riesgo_base + random.choice([-1, 0, 0, 1])))
                ats  = random.random() < prob_ats

                perfiles.append({
                    'nombre':    nombre,
                    'apellido':  ap,
                    'area':      area,
                    'puesto':    tipo_puesto,
                    'risk':      risk,
                    'ats':       ats,
                    'num':       f'PRUEBA-{idx+1:03d}',
                    'sexo':      random.choice(['M', 'F']),
                    'edad':      random.randint(22, 55),
                    'jornada':   random.choice(['diurno', 'mixto', 'tiempo_completo', 'nocturno']),
                    'contrato':  random.choice(['planta', 'temporal', 'honorarios']),
                })
                idx += 1

        self.stdout.write(f'Creando {len(perfiles)} trabajadores...')

        # ── Crear trabajadores, aplicaciones y resultados ────────────────
        niveles = ['nulo', 'bajo', 'medio', 'alto', 'muy_alto']
        dist = {n: 0 for n in niveles}
        ats_count = 0
        total_resultados = 0

        for p in perfiles:
            nombre_completo = f"PRUEBA {p['nombre']} {p['apellido']}"

            # 1) Trabajador
            t = Trabajador.objects.create(
                tenant            = tenant,
                nombre            = f"PRUEBA {p['nombre']}",
                apellido_paterno  = p['apellido'],
                num_empleado      = p['num'],
                area              = p['area'],
                tipo_puesto       = p['puesto'],
                tipo_contratacion = p['contrato'],
                tipo_jornada      = p['jornada'],
                sexo              = p['sexo'],
                edad              = p['edad'],
                activo            = True,
            )

            # 2) Guía V
            app_v = Aplicacion.objects.create(
                tenant=tenant, ciclo=ciclo, cuestionario=guia_v,
                trabajador=t, estado='completado', fecha_completado=timezone.now(),
            )
            resp_v = _respuestas_guia_v(guia_v, nombre_completo, p['area'], p['puesto'])
            RespuestaPregunta.objects.bulk_create([
                RespuestaPregunta(
                    tenant=tenant, aplicacion=app_v, pregunta_id=pid,
                    valor=val if isinstance(val, int) else None,
                    valor_texto=val if isinstance(val, str) else '',
                )
                for pid, val in resp_v.items()
            ])

            # 3) Guía I
            app_i = Aplicacion.objects.create(
                tenant=tenant, ciclo=ciclo, cuestionario=guia_i,
                trabajador=t, estado='completado', fecha_completado=timezone.now(),
            )
            resp_i = _respuestas_guia_i(guia_i, p['ats'])
            RespuestaPregunta.objects.bulk_create([
                RespuestaPregunta(tenant=tenant, aplicacion=app_i, pregunta_id=pid, valor=val)
                for pid, val in resp_i.items()
            ])

            # 4) Guía III
            es_sup = p['puesto'] in ('Supervisor', 'Gerente')
            resp_iii = _respuestas_guia_iii(guia_iii, p['risk'], es_sup)
            app_iii = Aplicacion.objects.create(
                tenant=tenant, ciclo=ciclo, cuestionario=guia_iii,
                trabajador=t, estado='completado', fecha_completado=timezone.now(),
            )
            RespuestaPregunta.objects.bulk_create([
                RespuestaPregunta(tenant=tenant, aplicacion=app_iii, pregunta_id=pid, valor=val)
                for pid, val in resp_iii.items()
            ])

            # 5) Calcular resultados Guía I y III
            for app in [app_i, app_iii]:
                app.refresh_from_db()
                datos = calcular_resultado(app)
                if datos:
                    _calcular_y_guardar(app, datos)
                    total_resultados += 1

            nivel = niveles[p['risk']]
            dist[nivel] += 1
            if p['ats']:
                ats_count += 1

        # ── Resumen ─────────────────────────────────────────────────────
        self.stdout.write(self.style.SUCCESS(
            f'OK: {len(perfiles)} trabajadores, {total_resultados} resultados calculados'
        ))
        self.stdout.write('Distribucion Guia III:')
        total = len(perfiles)
        for nivel, count in dist.items():
            pct = int(count / total * 100)
            self.stdout.write(f'  {nivel:10s} {count:3d}  ({pct}%)')
        self.stdout.write(f'Casos ATS (Guia I): {ats_count}')
        self.stdout.write('Login: pruebabenja')
