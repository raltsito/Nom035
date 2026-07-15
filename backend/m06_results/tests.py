"""
Pruebas del motor de calificación NOM-035 (m06_results.scoring) y de las
utilidades de muestra/confidencialidad.

Los cuestionarios de prueba reproducen la estructura real de producción:
Guía III = 14 bloques de captura con 72 ítems de frecuencia + 2 filtros
(atiende clientes / es jefe); Guía I = 4 secciones Sí/No.
"""
from unittest.mock import MagicMock

from django.test import SimpleTestCase

from core.confidencialidad import grupo_reservado
from m00_onboarding.views import _estratos_restos_mayores, _muestra
from .scoring import (
    VERSION_MOTOR,
    _calcular_guia_i,
    _calcular_guia_iii,
    _categoria_por_rangos,
    _CORTES_CATEGORIA,
    _CORTES_DOMINIO,
    _CORTES_FINAL,
    _DIMENSIONES,
    _GUIA_III_INVERSOS,
    calcular_resultado,
    puntaje_item_guia_iii,
)

# ---------------------------------------------------------------------------
# Estructura real del cuestionario Guía III (bloques → nº de ítems)
# ---------------------------------------------------------------------------
_BLOQUES_III = [
    ('D1', 5), ('D2', 3), ('D3', 4), ('D4', 4), ('D5', 6), ('D6', 6),
    ('D7', 2), ('D8', 6), ('D9', 5), ('D10', 5), ('D11', 10), ('D12', 8),
    ('D13', 4), ('D14', 4),
]
_FILTRO_ID = {'D13': 1001, 'D14': 1002}


def _pregunta(pid, tipo='frecuencia', orden=1):
    p = MagicMock()
    p.id = pid
    p.tipo_respuesta = tipo
    p.orden = orden
    return p


def _respuesta(valor):
    r = MagicMock()
    r.valor = valor
    r.valor_texto = ''
    return r


def _dominio(clave, nombre, preguntas):
    d = MagicMock()
    d.id = abs(hash(clave)) % 10000
    d.clave = clave
    d.nombre = nombre
    d.preguntas.all.return_value = preguntas
    d.preguntas.prefetch_related.return_value = d.preguntas
    return d


def _app(clave_guia, dominios):
    app = MagicMock()
    app.cuestionario.clave = clave_guia
    app.cuestionario.dominios.prefetch_related.return_value.all.return_value = dominios
    return app


def _app_guia_iii():
    """Cuestionario Guía III completo. Los ids de pregunta de los ítems de
    frecuencia son su número oficial (1-72); filtros: 1001 (D13) y 1002 (D14)."""
    dominios = []
    item = 1
    for clave, n_items in _BLOQUES_III:
        preguntas = []
        if clave in _FILTRO_ID:
            preguntas.append(_pregunta(_FILTRO_ID[clave], 'si_no', orden=0))
        for orden in range(1, n_items + 1):
            preguntas.append(_pregunta(item, 'frecuencia', orden=orden))
            item += 1
        dominios.append(_dominio(clave, f'Bloque {clave}', preguntas))
    return _app('III', dominios)


def _respuestas_iii(valores, filtro_clientes=1, filtro_jefe=1):
    """valores: dict {item 1-72: valor crudo 0-4} (los faltantes se omiten).
    filtro_*: 1=Sí, 0=No, None=sin responder (se omite del dict)."""
    respuestas = {item: _respuesta(v) for item, v in valores.items()}
    if filtro_clientes is not None:
        respuestas[_FILTRO_ID['D13']] = _respuesta(filtro_clientes)
    if filtro_jefe is not None:
        respuestas[_FILTRO_ID['D14']] = _respuesta(filtro_jefe)
    return respuestas


def _valores_completos(valor_directo=0, valor_inverso=4, items=range(1, 73)):
    """Valores crudos que producen el mismo puntaje recodificado en todos los
    ítems: con los defaults (0 directo, 4 inverso) el puntaje es 0 en todo."""
    return {
        i: (valor_inverso if i in _GUIA_III_INVERSOS else valor_directo)
        for i in items
    }


def _valores_puntaje_objetivo(total):
    """Valores crudos para que Cfinal (72 ítems aplicables) sea `total`:
    reparte el puntaje recodificado de 4 en 4 empezando por el ítem 1."""
    valores = _valores_completos()  # todo en 0 puntos
    restante = total
    for i in range(1, 73):
        if restante <= 0:
            break
        p = min(4, restante)
        # puntaje recodificado p → valor crudo
        valores[i] = (4 - p) if i in _GUIA_III_INVERSOS else p
        restante -= p
    assert restante == 0, 'objetivo inalcanzable'
    return valores


def _resultado_iii(valores, filtro_clientes=1, filtro_jefe=1):
    return _calcular_guia_iii(_app_guia_iii(), _respuestas_iii(valores, filtro_clientes, filtro_jefe))


# ---------------------------------------------------------------------------
# Recodificación (Tabla 5)
# ---------------------------------------------------------------------------

class TestRecodificacionTabla5(SimpleTestCase):

    ITEMS_INVERSOS_OFICIALES = (
        {1, 4} | set(range(23, 29)) | {30} | set(range(31, 54)) | {55, 56, 57}
    )

    def test_lista_oficial_de_inversos(self):
        """La constante coincide exactamente con la Tabla 5 del DOF
        (29 y 54 directos; 57 invertido)."""
        self.assertEqual(set(_GUIA_III_INVERSOS), self.ITEMS_INVERSOS_OFICIALES)

    def test_recodificacion_los_72_items(self):
        for item in range(1, 73):
            for valor in range(0, 5):
                esperado = 4 - valor if item in self.ITEMS_INVERSOS_OFICIALES else valor
                self.assertEqual(
                    puntaje_item_guia_iii(item, valor), esperado,
                    f'ítem {item}, valor {valor}')

    def test_extremos_directo_e_inverso(self):
        self.assertEqual(puntaje_item_guia_iii(2, 0), 0)   # directo
        self.assertEqual(puntaje_item_guia_iii(2, 4), 4)
        self.assertEqual(puntaje_item_guia_iii(1, 0), 4)   # inverso
        self.assertEqual(puntaje_item_guia_iii(1, 4), 0)


# ---------------------------------------------------------------------------
# Puntos de corte (todas las fronteras)
# ---------------------------------------------------------------------------

class TestCortesOficiales(SimpleTestCase):

    def _fronteras(self, cortes):
        """[(puntaje, nivel_esperado)] justo abajo y en cada límite."""
        casos = []
        niveles = [n for _, n in cortes] + ['muy_alto']
        limites = [l for l, _ in cortes]
        for idx, lim in enumerate(limites):
            casos.append((lim - 1, niveles[idx]))
            casos.append((lim, niveles[idx + 1]))
        return casos

    def test_fronteras_cfinal(self):
        esperados = [(49, 'nulo'), (50, 'bajo'), (74, 'bajo'), (75, 'medio'),
                     (98, 'medio'), (99, 'alto'), (139, 'alto'), (140, 'muy_alto')]
        for puntaje, nivel in esperados:
            self.assertEqual(_categoria_por_rangos(puntaje, _CORTES_FINAL), nivel, puntaje)

    def test_fronteras_todas_las_categorias(self):
        for nombre, cortes in _CORTES_CATEGORIA.items():
            for puntaje, nivel in self._fronteras(cortes):
                self.assertEqual(
                    _categoria_por_rangos(puntaje, cortes), nivel,
                    f'{nombre} @ {puntaje}')

    def test_fronteras_todos_los_dominios(self):
        for nombre, cortes in _CORTES_DOMINIO.items():
            for puntaje, nivel in self._fronteras(cortes):
                self.assertEqual(
                    _categoria_por_rangos(puntaje, cortes), nivel,
                    f'{nombre} @ {puntaje}')

    def test_cfinal_integrado_en_fronteras(self):
        """Cuestionarios completos con Cfinal exactamente en cada frontera."""
        for objetivo, nivel in [(49, 'nulo'), (50, 'bajo'), (74, 'bajo'), (75, 'medio'),
                                (98, 'medio'), (99, 'alto'), (139, 'alto'), (140, 'muy_alto')]:
            r = _resultado_iii(_valores_puntaje_objetivo(objetivo))
            self.assertTrue(r['es_valido'])
            self.assertEqual(r['puntaje_total'], objetivo)
            self.assertEqual(r['categoria'], nivel, f'Cfinal={objetivo}')


# ---------------------------------------------------------------------------
# Cuestionarios extremos e integración Tabla 6
# ---------------------------------------------------------------------------

class TestGuiaIIICompleta(SimpleTestCase):

    def test_totalmente_protector(self):
        r = _resultado_iii(_valores_completos(valor_directo=0, valor_inverso=4))
        self.assertTrue(r['es_valido'])
        self.assertEqual(r['puntaje_total'], 0)
        self.assertEqual(r['puntaje_max'], 288)  # 72 ítems × 4
        self.assertEqual(r['categoria'], 'nulo')
        for d in r['dominios_oficiales']:
            self.assertEqual(d['categoria'], 'nulo', d['nombre'])
        for c in r['categorias']:
            self.assertEqual(c['categoria'], 'nulo', c['nombre'])

    def test_maximo_riesgo(self):
        r = _resultado_iii(_valores_completos(valor_directo=4, valor_inverso=0))
        self.assertTrue(r['es_valido'])
        self.assertEqual(r['puntaje_total'], 288)
        self.assertEqual(r['categoria'], 'muy_alto')
        for d in r['dominios_oficiales']:
            self.assertEqual(d['categoria'], 'muy_alto', d['nombre'])
        for c in r['categorias']:
            self.assertEqual(c['categoria'], 'muy_alto', c['nombre'])

    def test_maximos_por_dominio_tabla6(self):
        """Nº de ítems por dominio oficial según la Tabla 6 (con filtros Sí)."""
        esperados = {
            'Condiciones en el ambiente de trabajo':               20,  # ítems 1-5
            'Carga de trabajo':                                    60,  # 6-16 + 65-68
            'Falta de control sobre el trabajo':                   40,  # 23-30 + 35-36
            'Jornada de trabajo':                                  8,   # 17-18
            'Interferencia en la relación trabajo-familia':        16,  # 19-22
            'Liderazgo':                                           36,  # 31-34 + 37-41
            'Relaciones en el trabajo':                            36,  # 42-46 + 69-72
            'Violencia':                                           32,  # 57-64
            'Reconocimiento del desempeño':                        24,  # 47-52
            'Insuficiente sentido de pertenencia e inestabilidad': 16,  # 53-56
        }
        r = _resultado_iii(_valores_completos())
        maximos = {d['nombre']: d['puntaje_max'] for d in r['dominios_oficiales']}
        self.assertEqual(maximos, esperados)
        self.assertEqual(sum(maximos.values()), 288)

    def test_categorias_suman_sus_dominios(self):
        valores = {i: 2 for i in range(1, 73)}  # crudo 2 → recodificado 2 en todos
        r = _resultado_iii(valores)
        dominios = {d['nombre']: d['puntaje'] for d in r['dominios_oficiales']}
        categorias = {c['nombre']: c['puntaje'] for c in r['categorias']}
        self.assertEqual(categorias['Ambiente de trabajo'],
                         dominios['Condiciones en el ambiente de trabajo'])
        self.assertEqual(categorias['Factores propios de la actividad'],
                         dominios['Carga de trabajo'] + dominios['Falta de control sobre el trabajo'])
        self.assertEqual(categorias['Liderazgo y relaciones en el trabajo'],
                         dominios['Liderazgo'] + dominios['Relaciones en el trabajo'] + dominios['Violencia'])
        self.assertEqual(sum(categorias.values()), r['puntaje_total'])
        # Clasificación de cada categoría con sus cortes oficiales
        for c in r['categorias']:
            self.assertEqual(
                c['categoria'],
                _categoria_por_rangos(c['puntaje'], _CORTES_CATEGORIA[c['nombre']]))

    def test_dimensiones_25_descriptivas_sin_nivel(self):
        r = _resultado_iii(_valores_completos(valor_directo=4, valor_inverso=0))
        dims = r['dimensiones']
        self.assertEqual(len(dims), 25)
        # Cubren los 72 ítems exactamente una vez
        todos = [i for _, _, _, items in _DIMENSIONES for i in items]
        self.assertEqual(sorted(todos), list(range(1, 73)))
        self.assertEqual(sum(d['puntaje_max'] for d in dims), 288)
        for d in dims:
            self.assertNotIn('categoria', d)   # sin nivel: solo descriptivo
            self.assertIn('nota', d)
        # Asignaciones verificadas contra el DOF (Tabla 6)
        por_nombre = {d['nombre']: d for d in dims}
        self.assertEqual(por_nombre['Inestabilidad laboral']['items'], [53, 54])
        self.assertEqual(por_nombre['Limitado sentido de pertenencia']['items'], [55, 56])
        self.assertEqual(por_nombre['Condiciones peligrosas e inseguras']['items'], [1, 3])
        self.assertEqual(por_nombre['Violencia laboral']['items'], list(range(57, 65)))


# ---------------------------------------------------------------------------
# Validación: faltantes, rangos, filtros condicionados
# ---------------------------------------------------------------------------

class TestValidacionGuiaIII(SimpleTestCase):

    def test_faltante_obligatorio_invalida(self):
        valores = _valores_completos()
        del valores[10]
        r = _resultado_iii(valores)
        self.assertFalse(r['es_valido'])
        self.assertIsNone(r['categoria'])         # nunca se clasifica
        self.assertIsNone(r['puntaje_total'])     # nunca se imputa 0
        faltantes = [f['item'] for f in r['validacion']['reactivos_faltantes']]
        self.assertIn(10, faltantes)

    def test_fuera_de_rango_invalida(self):
        valores = _valores_completos()
        valores[7] = 9
        r = _resultado_iii(valores)
        self.assertFalse(r['es_valido'])
        fuera = [f['item'] for f in r['validacion']['reactivos_fuera_de_rango']]
        self.assertIn(7, fuera)

    def test_filtro_no_excluye_condicionados(self):
        """Filtros 'No' con condicionados vacíos: válido; 65-72 no suman."""
        valores = _valores_completos(items=range(1, 65))  # solo 1-64
        r = _resultado_iii(valores, filtro_clientes=0, filtro_jefe=0)
        self.assertTrue(r['es_valido'])
        self.assertEqual(r['puntaje_max'], 256)  # 64 ítems × 4
        carga = next(d for d in r['dominios_oficiales'] if d['nombre'] == 'Carga de trabajo')
        self.assertEqual(carga['puntaje_max'], 44)  # sin 65-68

    def test_filtro_si_condicionado_faltante_invalida(self):
        valores = _valores_completos()
        del valores[66]
        r = _resultado_iii(valores, filtro_clientes=1)
        self.assertFalse(r['es_valido'])

    def test_filtro_faltante_invalida(self):
        valores = _valores_completos(items=range(1, 65))
        r = _resultado_iii(valores, filtro_clientes=None, filtro_jefe=0)
        self.assertFalse(r['es_valido'])
        self.assertTrue(any('Filtro' in e for e in r['validacion']['errores_criticos']))

    def test_filtro_no_con_condicionados_contestados_advierte_y_no_suma(self):
        valores = _valores_completos(valor_directo=4, valor_inverso=0, items=range(1, 65))
        valores.update({i: 4 for i in range(65, 73)})  # contestados "de más"
        r = _resultado_iii(valores, filtro_clientes=0, filtro_jefe=0)
        self.assertTrue(r['es_valido'])
        self.assertEqual(len(r['validacion']['inconsistencias_filtros']), 8)
        self.assertTrue(r['validacion']['advertencias'])
        self.assertEqual(r['puntaje_total'], 256)  # 65-72 excluidos de la suma

    def test_cuestionario_vacio_invalida(self):
        r = _calcular_guia_iii(_app_guia_iii(), {})
        self.assertFalse(r['es_valido'])
        self.assertIsNone(r['categoria'])


# ---------------------------------------------------------------------------
# Guía I — ATS (criterios independientes por sección)
# ---------------------------------------------------------------------------

class TestGuiaI(SimpleTestCase):

    SECCIONES = [('D1', 6), ('D2', 2), ('D3', 7), ('D4', 5)]

    def _app_y_respuestas(self, d1=0, d2=0, d3=0, d4=0, omitir=()):
        """dN = nº de "Sí" en la sección; `omitir`: ids de pregunta sin responder."""
        dominios, respuestas = [], {}
        pid = 1
        positivos = {'D1': d1, 'D2': d2, 'D3': d3, 'D4': d4}
        for clave, n in self.SECCIONES:
            pregs = []
            for i in range(n):
                p = _pregunta(pid, 'si_no', orden=i + 1)
                pregs.append(p)
                if pid not in omitir:
                    respuestas[pid] = _respuesta(1 if i < positivos[clave] else 0)
                pid += 1
            dominios.append(_dominio(clave, f'Sección {clave}', pregs))
        return _app('I', dominios), respuestas

    def test_sin_acontecimiento(self):
        app, resp = self._app_y_respuestas(d1=0, d2=1, d3=5, d4=3)
        r = _calcular_guia_i(app, resp)
        self.assertTrue(r['es_valido'])
        self.assertFalse(r['requiere_atencion'])
        self.assertFalse(r['guia_i']['reporta_ats'])

    def test_criterio_ii(self):
        app, resp = self._app_y_respuestas(d1=1, d2=1)
        r = _calcular_guia_i(app, resp)
        self.assertTrue(r['requiere_atencion'])
        self.assertTrue(r['guia_i']['cumple_criterio_ii'])
        self.assertFalse(r['guia_i']['cumple_criterio_iii'])

    def test_criterio_iii_umbral_tres(self):
        app, resp = self._app_y_respuestas(d1=1, d3=2)
        self.assertFalse(_calcular_guia_i(app, resp)['requiere_atencion'])
        app, resp = self._app_y_respuestas(d1=1, d3=3)
        r = _calcular_guia_i(app, resp)
        self.assertTrue(r['requiere_atencion'])
        self.assertTrue(r['guia_i']['cumple_criterio_iii'])

    def test_criterio_iv_umbral_dos(self):
        app, resp = self._app_y_respuestas(d1=1, d4=1)
        self.assertFalse(_calcular_guia_i(app, resp)['requiere_atencion'])
        app, resp = self._app_y_respuestas(d1=1, d4=2)
        self.assertTrue(_calcular_guia_i(app, resp)['requiere_atencion'])

    def test_no_suma_combinada_de_secciones(self):
        """D3=2 y D4=1 suman 3 'Sí' pero ninguna sección alcanza su umbral."""
        app, resp = self._app_y_respuestas(d1=1, d3=2, d4=1)
        r = _calcular_guia_i(app, resp)
        self.assertFalse(r['requiere_atencion'])
        self.assertEqual(r['categoria'], 'sin_indicadores')

    def test_acontecimiento_sin_criterios_posteriores(self):
        app, resp = self._app_y_respuestas(d1=2)
        r = _calcular_guia_i(app, resp)
        self.assertTrue(r['guia_i']['reporta_ats'])
        self.assertFalse(r['requiere_atencion'])

    def test_seccion_i_incompleta_invalida(self):
        app, resp = self._app_y_respuestas(d1=0, omitir=(3,))
        r = _calcular_guia_i(app, resp)
        self.assertFalse(r['es_valido'])
        self.assertIsNone(r['requiere_atencion'])
        self.assertIsNone(r['categoria'])

    def test_con_ats_secciones_ii_iv_obligatorias(self):
        """Si hubo acontecimiento, un faltante en II-IV invalida (no cuenta como 'No')."""
        app, resp = self._app_y_respuestas(d1=1, omitir=(7,))  # 7 = 1a pregunta de D2
        r = _calcular_guia_i(app, resp)
        self.assertFalse(r['es_valido'])

    def test_sin_ats_secciones_ii_iv_opcionales(self):
        """GR.I inciso a: si toda la Sección I es 'No', II-IV pueden omitirse."""
        omitidas = tuple(range(7, 21))  # todas las preguntas de D2-D4
        app, resp = self._app_y_respuestas(d1=0, omitir=omitidas)
        r = _calcular_guia_i(app, resp)
        self.assertTrue(r['es_valido'])
        self.assertEqual(r['categoria'], 'sin_indicadores')


# ---------------------------------------------------------------------------
# Punto de entrada, trazabilidad e idempotencia
# ---------------------------------------------------------------------------

class TestCalcularResultado(SimpleTestCase):

    def _app_completa(self):
        app = _app_guia_iii()
        respuestas = _respuestas_iii(_valores_completos(valor_directo=2, valor_inverso=2))
        app.respuestas.all.return_value = list(respuestas.values())
        for pid, r in respuestas.items():
            r.pregunta_id = pid
        return app

    def test_guia_v_retorna_none(self):
        app = MagicMock()
        app.cuestionario.clave = 'V'
        app.respuestas.all.return_value = []
        self.assertIsNone(calcular_resultado(app))

    def test_incluye_version_y_hash(self):
        r = calcular_resultado(self._app_completa())
        self.assertEqual(r['version_motor'], VERSION_MOTOR)
        self.assertEqual(len(r['hash_respuestas']), 64)

    def test_idempotencia(self):
        app = self._app_completa()
        r1 = calcular_resultado(app)
        r2 = calcular_resultado(app)
        self.assertEqual(r1['hash_respuestas'], r2['hash_respuestas'])
        self.assertEqual(r1['puntaje_total'], r2['puntaje_total'])
        self.assertEqual(r1['categoria'], r2['categoria'])

    def test_hash_cambia_si_cambia_una_respuesta(self):
        app = self._app_completa()
        h1 = calcular_resultado(app)['hash_respuestas']
        lista = app.respuestas.all.return_value
        lista[0].valor = 3 if lista[0].valor != 3 else 1
        h2 = calcular_resultado(app)['hash_respuestas']
        self.assertNotEqual(h1, h2)


# ---------------------------------------------------------------------------
# Muestra (Ecuación 1) y estratificación por restos mayores
# ---------------------------------------------------------------------------

class TestMuestra(SimpleTestCase):

    def test_ejemplo_oficial_n_100(self):
        """Ejemplo textual de la NOM (GR.III III.1): N=100 → n=80."""
        self.assertEqual(_muestra(100), 80)

    def test_valores_conocidos(self):
        self.assertEqual(_muestra(0), 0)
        self.assertEqual(_muestra(1), 1)
        for N in (60, 200, 500, 1000, 5000):
            n = _muestra(N)
            exacto = (0.9604 * N) / (0.0025 * (N - 1) + 0.9604)
            self.assertGreaterEqual(n, exacto)          # redondeo hacia arriba
            self.assertLess(n - exacto, 1)
            self.assertLessEqual(n, N)

    def test_restos_mayores_suma_exacta(self):
        casos = [
            (80, [52, 48]),
            (80, [33, 33, 34]),
            (218, [120, 90, 60, 45, 30, 25, 20, 15, 10, 85]),
            (7,  [1, 1, 1, 1, 1, 1, 1, 100]),
        ]
        for n, tamanos in casos:
            asignados = _estratos_restos_mayores(n, sum(tamanos), tamanos)
            self.assertEqual(sum(asignados), min(n, sum(tamanos)), (n, tamanos))
            for a, t in zip(asignados, tamanos):
                self.assertLessEqual(a, t)

    def test_restos_mayores_proporcional_por_sexo(self):
        # 52% hombres / 48% mujeres, n=80 → 42/38 (fracción mayor a hombres)
        self.assertEqual(_estratos_restos_mayores(80, 100, [52, 48]), [42, 38])

    def test_restos_mayores_no_excede_poblacion(self):
        self.assertEqual(sum(_estratos_restos_mayores(50, 30, [20, 10])), 30)


# ---------------------------------------------------------------------------
# Confidencialidad de grupos pequeños
# ---------------------------------------------------------------------------

class TestConfidencialidad(SimpleTestCase):

    def test_umbral_por_defecto(self):
        self.assertTrue(grupo_reservado(0))
        self.assertTrue(grupo_reservado(4))
        self.assertFalse(grupo_reservado(5))
        self.assertFalse(grupo_reservado(50))

    def test_umbral_configurable(self):
        with self.settings(NOM035_UMBRAL_CONFIDENCIALIDAD=10):
            self.assertTrue(grupo_reservado(9))
            self.assertFalse(grupo_reservado(10))
