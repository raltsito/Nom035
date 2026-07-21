"""Pruebas de la corrección de fidelidad (jul-2026, 2ª ronda) del Informe
Diagnóstico NOM-035, puntos 3 y 4 detectados en el informe de Saltillo:

1. Anexo A.T.2 (Guía I): las secciones condicionadas II-IV solo incluyen
   aplicaciones elegibles (`detalle.guia_i.reporta_ats == True`), en vez de
   contar cualquier respuesta residual almacenada. Ver
   `documents.views._ats_desglose`.
2. Denominadores demográficos: `_distribucion_simple` ya no mezcla N_válido
   (categorías) con N_total (fila "Sin dato") en la misma tabla.

No se modifica `m06_results/scoring.py`: el motor de calificación ya estaba
correcto (0 discrepancias verificadas en la auditoría previa).
"""
from datetime import date

from django.core.management import call_command
from django.test import SimpleTestCase, TestCase

from documents.views import _ats_desglose, _distribucion_simple


# ---------------------------------------------------------------------------
# Corrección 2 — denominadores demográficos (función pura, sin BD)
# ---------------------------------------------------------------------------
class TestDistribucionSimpleNoMezclaDenominadores(SimpleTestCase):
    """Reproduce la proporción real de 'Tiempo en el puesto actual' de
    Saltillo-ciclo 2026 (233 válidos + 14 faltantes = 247)."""

    def _valores_tiempo_puesto(self):
        return (
            ['Menos de 1 año'] * 74 + ['1 a 3 años'] * 58 + ['3 a 5 años'] * 38
            + ['5 a 10 años'] * 38 + ['Más de 10 años'] * 25 + [None] * 14
        )

    def test_categorias_validas_se_calculan_solo_sobre_n_valido(self):
        d = _distribucion_simple(self._valores_tiempo_puesto())
        for fila in d['datos']:
            self.assertAlmostEqual(
                fila['pct_preciso'], fila['count'] / d['n_valido'] * 100, places=6,
                msg=f"{fila['label']} no usa N_valido como denominador")

    def test_sin_dato_no_aparece_como_categoria(self):
        d = _distribucion_simple(self._valores_tiempo_puesto())
        labels = [f['label'] for f in d['datos']]
        self.assertNotIn('Sin dato', labels)
        self.assertEqual(len(d['datos']), 5)

    def test_suma_de_categorias_validas_igual_a_n_valido(self):
        d = _distribucion_simple(self._valores_tiempo_puesto())
        self.assertEqual(sum(f['count'] for f in d['datos']), d['n_valido'])

    def test_n_valido_mas_n_faltante_igual_a_n_total(self):
        d = _distribucion_simple(self._valores_tiempo_puesto())
        self.assertEqual(d['n_valido'] + d['n_faltante'], d['n_total'])

    def test_porcentajes_visuales_redondeados_suman_100(self):
        d = _distribucion_simple(self._valores_tiempo_puesto())
        self.assertEqual(sum(f['pct'] for f in d['datos']), 100)

    def test_cifras_esperadas_saltillo_tiempo_en_el_puesto(self):
        d = _distribucion_simple(self._valores_tiempo_puesto())
        self.assertEqual(d['n_total'], 247)
        self.assertEqual(d['n_valido'], 233)
        self.assertEqual(d['n_faltante'], 14)
        self.assertEqual(d['pct_faltante'], 5.7)
        esperado = {
            'Menos de 1 año': (74, 32), '1 a 3 años': (58, 25),
            '3 a 5 años': (38, 16), '5 a 10 años': (38, 16),
            'Más de 10 años': (25, 11),
        }
        obtenido = {f['label']: (f['count'], f['pct']) for f in d['datos']}
        self.assertEqual(obtenido, esperado)

    def test_cifras_esperadas_saltillo_experiencia_laboral(self):
        valores = (
            ['Más de 10 años'] * 78 + ['5 a 10 años'] * 55 + ['1 a 3 años'] * 51
            + ['3 a 5 años'] * 33 + ['Menos de 1 año'] * 29 + [None] * 1
        )
        d = _distribucion_simple(valores)
        self.assertEqual(d['n_total'], 247)
        self.assertEqual(d['n_valido'], 246)
        self.assertEqual(d['n_faltante'], 1)
        self.assertEqual(d['pct_faltante'], 0.4)
        esperado = {
            'Más de 10 años': (78, 32), '5 a 10 años': (55, 22),
            '1 a 3 años': (51, 21), '3 a 5 años': (33, 13),
            'Menos de 1 año': (29, 12),
        }
        obtenido = {f['label']: (f['count'], f['pct']) for f in d['datos']}
        self.assertEqual(obtenido, esperado)

    def test_sin_faltantes_no_reporta_pct_faltante(self):
        d = _distribucion_simple(['A'] * 5 + ['B'] * 5)
        self.assertEqual(d['n_faltante'], 0)
        self.assertEqual(d['n_valido'], 10)
        self.assertEqual(d['n_total'], 10)


# ---------------------------------------------------------------------------
# Corrección 1 — Anexo A.T.2 (requiere BD: Aplicacion/RespuestaPregunta/
# ResultadoAplicacion reales, calculados con el motor de producción).
# ---------------------------------------------------------------------------
class TestAtsDesgloseFiltraPorElegibilidad(TestCase):
    """Escenario mínimo equivalente al caso real detectado en Saltillo
    (folio T048): un trabajador con Sección I 100% negativa que conserva
    respuestas residuales en Sección II."""

    @classmethod
    def setUpTestData(cls):
        from accounts.models import User
        from tenants.models import Tenant
        from m00_onboarding.models import CicloNOM, Trabajador
        from m05_questionnaires.models import Aplicacion, Cuestionario, Pregunta, RespuestaPregunta
        from m06_results.services import calcular_ciclo

        if Cuestionario.objects.filter(clave__in=('I', 'III', 'V')).count() != 3:
            call_command('seed_cuestionarios')

        consultor = User.objects.filter(rol='super_admin').first()
        if consultor is None:
            consultor = User.objects.create(
                username='consultor_test_ats', email='consultor_test_ats@example.com',
                first_name='Consultor', last_name='Test', rol='super_admin',
            )
            consultor.set_unusable_password()
            consultor.save()

        cls.tenant = Tenant.objects.create(
            nombre='TEST ATS DESGLOSE', razon_social='TEST ATS DESGLOSE SA',
            rfc='TST010101TS2', giro='Pruebas', num_trabajadores=4, consultor=consultor,
        )
        cls.ciclo = CicloNOM.objects.create(
            tenant=cls.tenant, anio=2099, fecha_inicio=date(2099, 1, 1), estado='iniciado')

        guia_i = Cuestionario.objects.get(clave='I')
        preguntas = {
            (p.dominio.clave, p.orden): p
            for p in Pregunta.objects.filter(dominio__cuestionario=guia_i).select_related('dominio')
        }
        cls._n_por_seccion = {
            clave: sum(1 for k in preguntas if k[0] == clave) for clave in ('D1', 'D2', 'D3', 'D4')
        }

        def crear_trabajador(folio):
            return Trabajador.objects.create(
                tenant=cls.tenant, nombre=folio, apellido_paterno='Test',
                num_empleado=folio, sexo='F',
            )

        def crear_aplicacion(trabajador):
            return Aplicacion.objects.create(
                tenant=cls.tenant, ciclo=cls.ciclo, cuestionario=guia_i,
                trabajador=trabajador, estado='completado',
            )

        def responder(aplicacion, dominio_clave, valores):
            for orden, valor in enumerate(valores, start=1):
                p = preguntas[(dominio_clave, orden)]
                RespuestaPregunta.objects.create(
                    tenant=cls.tenant, aplicacion=aplicacion, pregunta=p, valor=valor)

        n = cls._n_por_seccion

        # T-NEG: Sección I 100% negativa, sin residuales (caso limpio).
        cls.t_neg = crear_trabajador('T-NEG')
        responder(crear_aplicacion(cls.t_neg), 'D1', [0] * n['D1'])

        # T-RESIDUAL (equivalente al folio T048 real de Saltillo): Sección I
        # 100% negativa, pero con respuestas residuales COMPLETAS en Sección
        # II (no faltan preguntas de D2 -- por eso scoring.py no lo invalida).
        cls.t_residual = crear_trabajador('T-RESIDUAL')
        ap_residual = crear_aplicacion(cls.t_residual)
        responder(ap_residual, 'D1', [0] * n['D1'])
        responder(ap_residual, 'D2', [0] * n['D2'])

        # T-ELEG-1 / T-ELEG-2: Sección I positiva (>=1 "Sí"), responden
        # II/III/IV completas -- población elegible real.
        cls.t_elegible_1 = crear_trabajador('T-ELEG-1')
        ap_e1 = crear_aplicacion(cls.t_elegible_1)
        responder(ap_e1, 'D1', [1] + [0] * (n['D1'] - 1))
        responder(ap_e1, 'D2', [0] * n['D2'])
        responder(ap_e1, 'D3', [0] * n['D3'])
        responder(ap_e1, 'D4', [0] * n['D4'])

        cls.t_elegible_2 = crear_trabajador('T-ELEG-2')
        ap_e2 = crear_aplicacion(cls.t_elegible_2)
        responder(ap_e2, 'D1', [1] + [0] * (n['D1'] - 1))
        responder(ap_e2, 'D2', [0] * n['D2'])
        responder(ap_e2, 'D3', [0] * n['D3'])
        responder(ap_e2, 'D4', [0] * n['D4'])

        resumen = calcular_ciclo(cls.tenant, cls.ciclo)
        assert resumen is not None, 'El escenario de prueba no dejó aplicaciones completadas'

    def _secciones(self):
        return {s['clave']: s for s in _ats_desglose(self.tenant, self.ciclo)['secciones']}

    def test_seccion_i_incluye_los_4_cuestionarios_validos(self):
        self.assertEqual(self._secciones()['D1']['n'], 4)

    def test_residual_no_entra_en_seccion_ii(self):
        seccion_ii = self._secciones()['D2']
        self.assertEqual(seccion_ii['n'], 2)  # solo T-ELEG-1 y T-ELEG-2
        total_respuestas = sum(f['t_si'] + f['t_no'] for f in seccion_ii['filas'])
        n_preguntas_d2 = self._n_por_seccion['D2']
        self.assertEqual(total_respuestas, 2 * n_preguntas_d2,
                          'Las respuestas residuales de T-RESIDUAL no deben sumar en D2')

    def test_secciones_ii_iii_iv_comparten_la_misma_poblacion_elegible(self):
        secciones = self._secciones()
        self.assertEqual(secciones['D2']['n'], secciones['D3']['n'])
        self.assertEqual(secciones['D3']['n'], secciones['D4']['n'])
        self.assertEqual(secciones['D2']['n'], 2)

    def test_resumen_y_anexo_tienen_denominadores_compatibles(self):
        d = _ats_desglose(self.tenant, self.ciclo)
        self.assertEqual(d['resumen']['muestra'], self._secciones()['D1']['n'])
        self.assertEqual(d['resumen']['con_ats'], self._secciones()['D2']['n'])
        self.assertEqual(d['resumen']['con_ats'], self._secciones()['D3']['n'])
        self.assertEqual(d['resumen']['con_ats'], self._secciones()['D4']['n'])

    def test_advertencia_tecnica_no_bloqueante_para_residual(self):
        d = _ats_desglose(self.tenant, self.ciclo)
        trabajadores_advertidos = {a['trabajador_id'] for a in d['advertencias_tecnicas']}
        self.assertIn(self.t_residual.id, trabajadores_advertidos)
        self.assertNotIn(self.t_neg.id, trabajadores_advertidos)
        self.assertNotIn(self.t_elegible_1.id, trabajadores_advertidos)

    def test_residual_no_cambia_reporta_ats_ni_requiere_atencion_ni_se_borra(self):
        from m05_questionnaires.models import RespuestaPregunta
        from m06_results.models import ResultadoAplicacion

        resultado = ResultadoAplicacion.objects.get(aplicacion__trabajador=self.t_residual)
        self.assertEqual(resultado.estatus_validacion, 'valido')
        self.assertFalse(resultado.detalle['guia_i']['reporta_ats'])
        self.assertIsNot(resultado.requiere_atencion, True)

        # Las respuestas residuales NO se eliminan ni modifican en BD.
        n_preguntas_d2 = self._n_por_seccion['D2']
        self.assertEqual(
            RespuestaPregunta.objects.filter(
                aplicacion__trabajador=self.t_residual, pregunta__dominio__clave='D2',
            ).count(),
            n_preguntas_d2,
        )


class TestNoRegresionSobreGuiaIII(TestCase):
    """Corrección 1 y 2 tocan solo `_ats_desglose`/`_distribucion_simple`
    (Guía I y demografía); Guía III (categorías/dominios/áreas/conclusiones)
    debe permanecer exactamente igual porque no se tocó `scoring.py` ni
    `report_data.py`."""

    @classmethod
    def setUpTestData(cls):
        import os
        os.environ['NOM035_PERMITIR_FIXTURE'] = '1'
        call_command('cargar_fixture_prueba')
        from tenants.models import Tenant
        from m00_onboarding.models import CicloNOM
        cls.tenant = Tenant.objects.get(rfc='PRU010101PRB')
        cls.ciclo = CicloNOM.objects.get(tenant=cls.tenant)

    def test_report_data_guia_iii_no_cambia(self):
        from documents.report_data import build_report_data
        rd = build_report_data(self.tenant, self.ciclo)
        self.assertTrue(rd['validaciones']['puede_emitirse'], rd['validaciones']['errores_criticos'])
        dist = rd['tablas']['distribucion_final']
        self.assertEqual(sum(f['n'] for f in dist['filas']), dist['n_valido'])
        self.assertEqual(len(rd['tablas']['categorias']['filas']), 5)
        self.assertEqual(len(rd['tablas']['dominios']['filas']), 10)

    def test_ats_desglose_no_persiste_ni_altera_resultados(self):
        """`_ats_desglose` es de solo lectura: no debe modificar ninguna fila
        de ResultadoAplicacion/ResultadoDominio ni de RespuestaPregunta."""
        from m06_results.models import ResultadoAplicacion, ResultadoDominio
        from m05_questionnaires.models import RespuestaPregunta

        antes = (
            ResultadoAplicacion.objects.filter(aplicacion__tenant=self.tenant).count(),
            ResultadoDominio.objects.filter(resultado__aplicacion__tenant=self.tenant).count(),
            RespuestaPregunta.objects.filter(aplicacion__tenant=self.tenant).count(),
        )
        _ats_desglose(self.tenant, self.ciclo)
        _distribucion_simple(['A', 'B', None])
        despues = (
            ResultadoAplicacion.objects.filter(aplicacion__tenant=self.tenant).count(),
            ResultadoDominio.objects.filter(resultado__aplicacion__tenant=self.tenant).count(),
            RespuestaPregunta.objects.filter(aplicacion__tenant=self.tenant).count(),
        )
        self.assertEqual(antes, despues)
