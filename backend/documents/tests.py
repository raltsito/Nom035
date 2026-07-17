"""
Pruebas del motor de composición ejecutiva (documents.report_data).

Se prueba la función PURA `componer_report_data(raw)` con datos sintéticos:
tarjetas, rankings con desempates, confidencialidad, faltantes críticos y
validaciones de bloqueo de emisión.
"""
from django.test import SimpleTestCase

from m06_results.scoring import _CATEGORIAS_OFICIALES, _DOMINIOS_OFICIALES
from .report_data import componer_report_data


def _persona(area, nivel, puntaje=80):
    return {'trabajador_id': 0, 'area': area, 'nivel': nivel,
            'puntaje': puntaje, 'puntaje_max': 288}


def _dom(nombre, nivel, area='Producción'):
    return {'nombre': nombre, 'nivel': nivel, 'puntaje': 10,
            'puntaje_max': 40, 'area': area}


def _cat(nombre, nivel):
    return {'nombre': nombre, 'nivel': nivel, 'puntaje': 10, 'puntaje_max': 40}


def _dominios_completos(parciales=None, nivel_resto='nulo'):
    """Completa una lista parcial de dominios individuales con el resto de
    los 10 oficiales en `nivel_resto` (la validación estructural exige los
    10 dominios cuando hay Guía III válida)."""
    parciales = list(parciales or [])
    presentes = {d['nombre'] for d in parciales}
    for nombre in _DOMINIOS_OFICIALES:
        if nombre not in presentes:
            parciales.append(_dom(nombre, nivel_resto))
    return parciales


def _raw(iii, dominios_ind=None, categorias_ind=None, demograficos=None,
         guia_i=None, poblacion=100, invalidos=0):
    n = len(iii)
    if categorias_ind is None:
        categorias_ind = [_cat(c, 'medio') for c in _CATEGORIAS_OFICIALES] * max(n, 1)
    if dominios_ind is None:
        dominios_ind = [_dom(d, 'medio') for d in _DOMINIOS_OFICIALES] * max(n, 1)
    return {
        'tenant_nombre': 'Planta Test',
        'ciclo_id': 1,
        'ciclo_anio': 2026,
        'fecha_corte': '2026-07-14',
        'poblacion': poblacion,
        'flujo': {'seleccionados': n + invalidos, 'iniciadas': n + invalidos,
                  'completadas': n + invalidos, 'excluidas': invalidos, 'validas': n},
        'iii': iii,
        'iii_invalidos': invalidos,
        'categorias_ind': categorias_ind,
        'dominios_ind': dominios_ind,
        'guia_i': guia_i or {'validos': n, 'invalidos': 0, 'reporta_ats': 0,
                             'requieren_atencion': 0, 'criterio_ii': 0,
                             'criterio_iii': 0, 'criterio_iv': 0},
        'demograficos': demograficos or [
            {'variable': 'Sexo', 'n_valido': n, 'n_faltante': 0},
        ],
    }


def _componer(raw, umbral_conf=5, umbral_faltantes=10.0):
    return componer_report_data(raw, umbral_conf=umbral_conf,
                                umbral_faltantes_pct=umbral_faltantes)


class TestTarjetas(SimpleTestCase):

    def _rd_basico(self):
        iii = ([_persona('A', 'nulo')] * 3 + [_persona('A', 'medio')] * 4
               + [_persona('A', 'alto')] * 2 + [_persona('A', 'muy_alto')])
        gi = {'validos': 10, 'invalidos': 0, 'reporta_ats': 3,
              'requieren_atencion': 2, 'criterio_ii': 1, 'criterio_iii': 1, 'criterio_iv': 0}
        return _componer(_raw(iii, guia_i=gi, poblacion=100))

    def test_sin_tarjeta_de_nivel_global(self):
        rd = self._rd_basico()
        self.assertNotIn('nivel_global', [t['id'] for t in rd['tarjetas']])

    def test_tarjetas_basicas_pobladas(self):
        rd = self._rd_basico()
        t = {x['id']: x for x in rd['tarjetas']}
        self.assertEqual(t['poblacion']['valor'], '100')
        self.assertEqual(t['muestra_minima']['valor'], '80')  # Ecuación 1, N=100
        self.assertEqual(t['validos']['valor'], '10')
        # 4 medio + 2 alto + 1 muy_alto = 7 (70%); alto+muy_alto = 3 (30%)
        self.assertEqual(t['medio_o_mas']['valor'], '7 (70.0%)')
        self.assertEqual(t['alto_o_muy_alto']['valor'], '3 (30.0%)')
        self.assertEqual(t['ats']['valor'], '2 (20.0%)')

    def test_validaciones_pasan_con_datos_consistentes(self):
        rd = self._rd_basico()
        self.assertTrue(rd['validaciones']['puede_emitirse'],
                        rd['validaciones']['errores_criticos'])

    def test_sin_validos_bloquea_emision(self):
        rd = _componer(_raw([]))
        self.assertFalse(rd['validaciones']['puede_emitirse'])
        self.assertTrue(any('hay_cuestionarios_validos' in e
                            for e in rd['validaciones']['errores_criticos']))


class TestRankingDominios(SimpleTestCase):

    def test_desempate_por_medio_o_superior(self):
        """Violencia y Liderazgo empatan en % Alto+Muy alto; gana el de mayor
        % Medio o superior."""
        dominios = (
            [_dom('Violencia', 'alto')] * 2 + [_dom('Violencia', 'medio')] * 2
            + [_dom('Violencia', 'nulo')] * 6
            + [_dom('Liderazgo', 'alto')] * 2 + [_dom('Liderazgo', 'nulo')] * 8
        )
        rd = _componer(_raw([_persona('A', 'medio')] * 10, dominios_ind=dominios))
        filas = rd['tablas']['dominios']['filas']
        self.assertEqual(filas[0]['nombre'], 'Violencia')   # 40% medio+ vs 20%
        self.assertEqual(filas[0]['prioridad'], 1)
        self.assertEqual(filas[1]['nombre'], 'Liderazgo')

    def test_desempate_final_por_orden_normativo(self):
        """Empate total → gana el que aparece primero en la Tabla 6."""
        dominios = ([_dom('Violencia', 'alto')] + [_dom('Violencia', 'nulo')] * 9
                    + [_dom('Carga de trabajo', 'alto')] + [_dom('Carga de trabajo', 'nulo')] * 9)
        rd = _componer(_raw([_persona('A', 'medio')] * 10, dominios_ind=dominios))
        filas = rd['tablas']['dominios']['filas']
        # Carga de trabajo precede a Violencia en el orden normativo
        self.assertEqual(filas[0]['nombre'], 'Carga de trabajo')

    def test_tarjeta_dominio_prioritario_es_rank_1(self):
        dominios = _dominios_completos(
            [_dom('Violencia', 'muy_alto')] * 6 + [_dom('Liderazgo', 'nulo')] * 6)
        rd = _componer(_raw([_persona('A', 'alto')] * 6, dominios_ind=dominios))
        t = {x['id']: x for x in rd['tarjetas']}
        self.assertEqual(t['dominio_prioritario']['valor'],
                         rd['tablas']['dominios']['filas'][0]['nombre'])
        self.assertTrue(rd['validaciones']['puede_emitirse'])


class TestAreasYConfidencialidad(SimpleTestCase):

    def test_area_pequena_se_reserva_y_no_rankea(self):
        iii = ([_persona('Producción', 'alto')] * 6
               + [_persona('Oficina', 'muy_alto')] * 2)   # n=2 < umbral 5
        rd = _componer(_raw(iii))
        areas = rd['tablas']['areas']
        self.assertEqual([a['nombre'] for a in areas['filas']], ['Producción'])
        self.assertEqual(areas['reservadas'][0]['nombre'], 'Oficina')
        self.assertEqual(areas['reservadas'][0]['n'], 2)
        # La tarjeta de área prioritaria NO usa el grupo reservado
        t = {x['id']: x for x in rd['tarjetas']}
        self.assertEqual(t['area_prioritaria']['valor'], 'Producción')
        self.assertTrue(rd['validaciones']['puede_emitirse'])

    def test_ranking_de_areas_por_pct_alto(self):
        iii = ([_persona('A', 'alto')] * 4 + [_persona('A', 'nulo')] * 4
               + [_persona('B', 'alto')] * 2 + [_persona('B', 'nulo')] * 6)
        rd = _componer(_raw(iii))
        filas = rd['tablas']['areas']['filas']
        self.assertEqual(filas[0]['nombre'], 'A')  # 50% vs 25%
        self.assertEqual(filas[0]['prioridad'], 1)


class TestFaltantesYExclusiones(SimpleTestCase):

    def test_variable_con_faltantes_criticos(self):
        demog = [
            {'variable': 'Sexo', 'n_valido': 10, 'n_faltante': 0},
            {'variable': 'Edad', 'n_valido': 6, 'n_faltante': 4},  # 40% > 10%
        ]
        rd = _componer(_raw([_persona('A', 'medio')] * 10, demograficos=demog))
        variables = [v['variable'] for v in rd['faltantes_criticos']['variables']]
        self.assertEqual(variables, ['Edad'])
        self.assertIn('Edad', rd['exclusiones']['variables_sin_grafica'])
        t = {x['id']: x for x in rd['tarjetas']}
        self.assertIn('Edad', t['faltantes']['detalle'])

    def test_invalidos_diferenciados_de_demograficos(self):
        rd = _componer(_raw([_persona('A', 'medio')] * 10, invalidos=3))
        self.assertEqual(rd['faltantes_criticos']['cuestionarios_invalidos_iii'], 3)
        t = {x['id']: x for x in rd['tarjetas']}
        self.assertIn('inválidos por reactivos faltantes', t['faltantes']['detalle'])

    def test_sin_faltantes_no_hay_tarjeta(self):
        rd = _componer(_raw([_persona('A', 'medio')] * 10))
        self.assertNotIn('faltantes', [t['id'] for t in rd['tarjetas']])


class TestTablas(SimpleTestCase):

    def test_distribucion_suma_n_y_pcts_100(self):
        iii = ([_persona('A', 'nulo')] * 5 + [_persona('A', 'bajo')] * 5
               + [_persona('A', 'medio')] * 5 + [_persona('A', 'alto')] * 5)
        rd = _componer(_raw(iii))
        dist = rd['tablas']['distribucion_final']
        self.assertEqual(sum(f['n'] for f in dist['filas']), 20)
        self.assertAlmostEqual(sum(f['pct'] or 0 for f in dist['filas']), 100.0, delta=0.5)
        self.assertEqual(dist['medio_o_mas']['n'], 10)
        self.assertEqual(dist['alto_o_muy_alto']['n'], 5)

    def test_tablas_llevan_denominador_y_nota(self):
        rd = _componer(_raw([_persona('A', 'medio')] * 6))
        for clave, tabla in rd['tablas'].items():
            self.assertIn('nota', tabla, clave)
            if clave != 'flujo_muestra':
                self.assertIn('denominador', tabla, clave)

    def test_matriz_respeta_ranking(self):
        dominios = ([_dom('Violencia', 'muy_alto')] * 6
                    + [_dom('Carga de trabajo', 'medio')] * 6
                    + [_dom('Liderazgo', 'nulo')] * 6)
        rd = _componer(_raw([_persona('A', 'alto')] * 6, dominios_ind=dominios))
        filas = rd['tablas']['matriz_intervencion']['filas']
        self.assertEqual([f['dominio'] for f in filas][:2], ['Violencia', 'Carga de trabajo'])
        self.assertEqual([f['prioridad'] for f in filas], sorted(f['prioridad'] for f in filas))
        self.assertEqual(filas[0]['tipo_prioridad'], 'Elevada')
        self.assertEqual(filas[1]['tipo_prioridad'], 'Programa de intervención')
        # Liderazgo (todo nulo) no genera renglón de intervención
        self.assertNotIn('Liderazgo', [f['dominio'] for f in filas])

    def test_categorias_cubren_las_definidas(self):
        cats = [_cat(c, 'medio') for c in _CATEGORIAS_OFICIALES] * 6
        rd = _componer(_raw([_persona('A', 'medio')] * 6, categorias_ind=cats))
        nombres = [f['nombre'] for f in rd['tablas']['categorias']['filas']]
        self.assertEqual(set(nombres), set(_CATEGORIAS_OFICIALES))

    def test_violencia_resumida(self):
        dominios = [_dom('Violencia', 'alto')] * 3 + [_dom('Violencia', 'nulo')] * 9
        rd = _componer(_raw([_persona('A', 'medio')] * 12, dominios_ind=dominios))
        viol = rd['tablas']['violencia']
        self.assertEqual(viol['n_valido'], 12)
        self.assertEqual(viol['pct_alto_o_muy_alto'], 25.0)
        self.assertIn('no sustituye una investigación', viol['nota'])
