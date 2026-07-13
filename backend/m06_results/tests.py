from unittest.mock import MagicMock, patch
from django.test import TestCase

from .scoring import (
    calcular_resultado,
    _calcular_guia_i,
    _calcular_guia_iii,
    _categoria_por_rangos,
    _CORTES_FINAL,
)


# ---------------------------------------------------------------------------
# Helpers para construir mocks de Aplicacion
# ---------------------------------------------------------------------------

def _pregunta(id, tipo='frecuencia', inversa=False, orden=1):
    p = MagicMock()
    p.id             = id
    p.tipo_respuesta = tipo
    p.inversa        = inversa
    p.orden          = orden
    return p


def _respuesta(valor):
    r = MagicMock()
    r.valor = valor
    return r


def _dominio(clave, nombre, preguntas):
    d = MagicMock()
    d.id     = hash(clave)
    d.clave  = clave
    d.nombre = nombre
    d.preguntas.all.return_value = preguntas
    d.preguntas.prefetch_related.return_value = d.preguntas
    return d


def _aplicacion_guia_i(dominios_data):
    """
    dominios_data: lista de (clave, nombre, [(id_pregunta, tipo, inversa), ...])
    """
    dominios = []
    for clave, nombre, preguntas_def in dominios_data:
        preguntas = [_pregunta(pid, tipo) for pid, tipo, _ in preguntas_def]
        dominios.append(_dominio(clave, nombre, preguntas))

    app = MagicMock()
    app.cuestionario.clave = 'I'
    app.cuestionario.dominios.prefetch_related.return_value.all.return_value = dominios
    return app


def _build_guia_iii_aplicacion(dominios_data):
    """
    dominios_data: lista de (clave, nombre, [(id, tipo, inversa), ...])
    """
    dominios = []
    for clave, nombre, preguntas_def in dominios_data:
        preguntas = [_pregunta(pid, tipo, inv) for pid, tipo, inv in preguntas_def]
        dominios.append(_dominio(clave, nombre, preguntas))

    app = MagicMock()
    app.cuestionario.clave = 'III'
    app.cuestionario.dominios.prefetch_related.return_value.all.return_value = dominios
    return app


# ---------------------------------------------------------------------------
# Tests — utilidad de rangos
# ---------------------------------------------------------------------------

class TestCategoriaPorRangos(TestCase):

    def test_nulo(self):
        self.assertEqual(_categoria_por_rangos(0, _CORTES_FINAL), 'nulo')
        self.assertEqual(_categoria_por_rangos(49, _CORTES_FINAL), 'nulo')

    def test_bajo(self):
        self.assertEqual(_categoria_por_rangos(50, _CORTES_FINAL), 'bajo')
        self.assertEqual(_categoria_por_rangos(74, _CORTES_FINAL), 'bajo')

    def test_medio(self):
        self.assertEqual(_categoria_por_rangos(75, _CORTES_FINAL), 'medio')
        self.assertEqual(_categoria_por_rangos(98, _CORTES_FINAL), 'medio')

    def test_alto(self):
        self.assertEqual(_categoria_por_rangos(99, _CORTES_FINAL), 'alto')
        self.assertEqual(_categoria_por_rangos(139, _CORTES_FINAL), 'alto')

    def test_muy_alto(self):
        self.assertEqual(_categoria_por_rangos(140, _CORTES_FINAL), 'muy_alto')
        self.assertEqual(_categoria_por_rangos(999, _CORTES_FINAL), 'muy_alto')


# ---------------------------------------------------------------------------
# Tests — Guía I
# ---------------------------------------------------------------------------

class TestGuiaI(TestCase):

    def _app_con_respuestas(self, d1_positivos, d2_si=0, d3_si=0, d4_si=0):
        """
        Construye aplicación Guía I con las 4 secciones reales (conteos de
        preguntas iguales a los de producción): D1 = Sección I (ATS, 6
        preguntas), D2 = Sección II (2), D3 = Sección III (7), D4 = Sección
        IV (5). *_si = cuántas preguntas de esa sección se responden "Sí".
        """
        d1_preguntas = [_pregunta(i, 'si_no') for i in range(1, 7)]
        d2_preguntas = [_pregunta(i, 'si_no') for i in range(7, 9)]
        d3_preguntas = [_pregunta(i, 'si_no') for i in range(9, 16)]
        d4_preguntas = [_pregunta(i, 'si_no') for i in range(16, 21)]

        dominios = [
            _dominio('D1', 'Seccion I', d1_preguntas),
            _dominio('D2', 'Seccion II', d2_preguntas),
            _dominio('D3', 'Seccion III', d3_preguntas),
            _dominio('D4', 'Seccion IV', d4_preguntas),
        ]

        app = MagicMock()
        app.cuestionario.clave = 'I'
        app.cuestionario.dominios.prefetch_related.return_value.all.return_value = dominios

        respuestas = {}
        for i, p in enumerate(d1_preguntas):
            respuestas[p.id] = _respuesta(1 if i < d1_positivos else 0)
        for i, p in enumerate(d2_preguntas):
            respuestas[p.id] = _respuesta(1 if i < d2_si else 0)
        for i, p in enumerate(d3_preguntas):
            respuestas[p.id] = _respuesta(1 if i < d3_si else 0)
        for i, p in enumerate(d4_preguntas):
            respuestas[p.id] = _respuesta(1 if i < d4_si else 0)

        return app, respuestas

    def test_positivo_por_seccion_ii(self):
        """D1≥1 y Sección II≥1 (III y IV en 0) → requiere_atencion=True."""
        app, respuestas = self._app_con_respuestas(d1_positivos=1, d2_si=1)
        result = _calcular_guia_i(app, respuestas)
        self.assertTrue(result['requiere_atencion'])
        self.assertEqual(result['categoria'], 'requiere_atencion')

    def test_seccion_iii_requiere_umbral_de_tres(self):
        """Sección III dispara sola solo con >=3 (no con 2)."""
        app, respuestas = self._app_con_respuestas(d1_positivos=1, d3_si=2)
        result = _calcular_guia_i(app, respuestas)
        self.assertFalse(result['requiere_atencion'])

        app, respuestas = self._app_con_respuestas(d1_positivos=1, d3_si=3)
        result = _calcular_guia_i(app, respuestas)
        self.assertTrue(result['requiere_atencion'])

    def test_seccion_iv_requiere_umbral_de_dos(self):
        """Sección IV dispara sola solo con >=2 (no con 1)."""
        app, respuestas = self._app_con_respuestas(d1_positivos=1, d4_si=1)
        result = _calcular_guia_i(app, respuestas)
        self.assertFalse(result['requiere_atencion'])

        app, respuestas = self._app_con_respuestas(d1_positivos=1, d4_si=2)
        result = _calcular_guia_i(app, respuestas)
        self.assertTrue(result['requiere_atencion'])

    def test_suma_combinada_no_sustituye_umbral_por_seccion(self):
        """Caso real encontrado en producción: la suma D2+D3+D4 llega a 2
        (aquí solo por D3=2) pero ninguna sección alcanza su propio umbral
        -> NO requiere atención. El criterio viejo (suma combinada >=2)
        marcaba esto como falso positivo."""
        app, respuestas = self._app_con_respuestas(d1_positivos=1, d3_si=2)
        result = _calcular_guia_i(app, respuestas)
        self.assertFalse(result['requiere_atencion'])
        self.assertEqual(result['categoria'], 'sin_indicadores')

    def test_d1_negativo(self):
        """Sin acontecimiento en D1 → requiere_atencion=False aunque haya síntomas."""
        app, respuestas = self._app_con_respuestas(d1_positivos=0, d2_si=1, d3_si=5, d4_si=3)
        result = _calcular_guia_i(app, respuestas)
        self.assertFalse(result['requiere_atencion'])
        self.assertEqual(result['categoria'], 'sin_indicadores')

    def test_sin_respuestas(self):
        """Trabajador que no respondió nada → sin_indicadores."""
        app, respuestas = self._app_con_respuestas(d1_positivos=0)
        result = _calcular_guia_i(app, respuestas)
        self.assertFalse(result['requiere_atencion'])
        self.assertEqual(result['categoria'], 'sin_indicadores')


# ---------------------------------------------------------------------------
# Tests — Guía III
# ---------------------------------------------------------------------------

class TestGuiaIII(TestCase):

    def _app_puntaje(self, puntaje_deseado):
        """
        Crea una aplicación Guía III con un solo dominio D1 y respuestas
        ajustadas para alcanzar el puntaje_deseado. Usa valor = 4 por
        pregunta. La inversión por ítem se desactiva (parcheada) en estos
        tests porque lo que se ejercita aquí es la clasificación por
        `_CORTES_FINAL`, no la tabla de inversión (que tiene sus propios
        tests en TestInversionItems).
        """
        n_preguntas = max(1, (puntaje_deseado + 3) // 4)
        preguntas   = [_pregunta(i, 'frecuencia', False, orden=i) for i in range(1, n_preguntas + 1)]

        dominio = _dominio('D1', 'Ambiente', preguntas)

        app = MagicMock()
        app.cuestionario.clave = 'III'
        app.cuestionario.dominios.prefetch_related.return_value.all.return_value = [dominio]

        # Distribuir puntaje_deseado entre las preguntas
        respuestas = {}
        restante = puntaje_deseado
        for p in preguntas:
            val = min(4, restante)
            respuestas[p.id] = _respuesta(val)
            restante -= val

        return app, respuestas

    @patch('m06_results.scoring._GUIA_III_INVERSOS', set())
    def test_nivel_nulo(self):
        app, respuestas = self._app_puntaje(10)
        result = _calcular_guia_iii(app, respuestas)
        self.assertEqual(result['categoria'], 'nulo')
        self.assertIsNone(result['requiere_atencion'])

    @patch('m06_results.scoring._GUIA_III_INVERSOS', set())
    def test_nivel_bajo(self):
        app, respuestas = self._app_puntaje(60)
        result = _calcular_guia_iii(app, respuestas)
        self.assertEqual(result['categoria'], 'bajo')

    @patch('m06_results.scoring._GUIA_III_INVERSOS', set())
    def test_nivel_medio(self):
        app, respuestas = self._app_puntaje(85)
        result = _calcular_guia_iii(app, respuestas)
        self.assertEqual(result['categoria'], 'medio')

    @patch('m06_results.scoring._GUIA_III_INVERSOS', set())
    def test_nivel_alto(self):
        app, respuestas = self._app_puntaje(110)
        result = _calcular_guia_iii(app, respuestas)
        self.assertEqual(result['categoria'], 'alto')

    @patch('m06_results.scoring._GUIA_III_INVERSOS', set())
    def test_nivel_muy_alto(self):
        app, respuestas = self._app_puntaje(150)
        result = _calcular_guia_iii(app, respuestas)
        self.assertEqual(result['categoria'], 'muy_alto')

    def test_d13_excluido_si_no_aplica(self):
        """D13 con filtro respondido 'No' no suma al puntaje total."""
        filtro  = _pregunta(100, 'si_no', orden=1)
        p65     = _pregunta(101, 'frecuencia', orden=1)
        p66     = _pregunta(102, 'frecuencia', orden=2)
        d13     = _dominio('D13', 'Clientes', [filtro, p65, p66])

        app = MagicMock()
        app.cuestionario.clave = 'III'
        app.cuestionario.dominios.prefetch_related.return_value.all.return_value = [d13]

        # Filtro respondido 'No' (valor=0)
        respuestas = {
            filtro.id: _respuesta(0),
            p65.id:    _respuesta(4),
            p66.id:    _respuesta(4),
        }
        result = _calcular_guia_iii(app, respuestas)
        # D13 excluido → puntaje total = 0
        self.assertEqual(result['puntaje_total'], 0)
        self.assertEqual(result['puntaje_max'], 0)

    def test_d13_incluido_si_aplica(self):
        """D13 con filtro respondido 'Sí' sí suma al puntaje total."""
        filtro = _pregunta(100, 'si_no', orden=1)
        p65    = _pregunta(101, 'frecuencia', orden=1)
        p66    = _pregunta(102, 'frecuencia', orden=2)
        d13    = _dominio('D13', 'Clientes', [filtro, p65, p66])

        app = MagicMock()
        app.cuestionario.clave = 'III'
        app.cuestionario.dominios.prefetch_related.return_value.all.return_value = [d13]

        respuestas = {
            filtro.id: _respuesta(1),
            p65.id:    _respuesta(3),
            p66.id:    _respuesta(2),
        }
        result = _calcular_guia_iii(app, respuestas)
        self.assertEqual(result['puntaje_total'], 5)
        self.assertEqual(result['puntaje_max'], 8)


# ---------------------------------------------------------------------------
# Tests — inversión por ítem oficial (Tabla 5) y dominios_oficiales (Tabla 6)
# ---------------------------------------------------------------------------

class TestInversionYDominiosOficiales(TestCase):

    def _resultado(self, dominios_data):
        """dominios_data: lista de (clave, nombre, [(id, orden), ...]) — todas
        preguntas tipo 'frecuencia'."""
        dominios = []
        respuestas = {}
        for clave, nombre, preguntas_def in dominios_data:
            preguntas = [_pregunta(pid, 'frecuencia', orden=orden) for pid, orden in preguntas_def]
            for pid, _ in preguntas_def:
                respuestas[pid] = _respuesta(1)
            dominios.append(_dominio(clave, nombre, preguntas))

        app = MagicMock()
        app.cuestionario.clave = 'III'
        app.cuestionario.dominios.prefetch_related.return_value.all.return_value = dominios
        return _calcular_guia_iii(app, respuestas)

    def test_d1_items_1_y_4_se_invierten(self):
        """D1-P1 (ítem 1) y D1-P4 (ítem 4) deben invertirse; P2, P3, P5 no."""
        result = self._resultado([
            ('D1', 'Ambiente', [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)]),
        ])
        d1 = next(d for d in result['dominios'] if d['dominio_clave'] == 'D1')
        # valor=1 en todas: item1 y item4 invertidos → 4-1=3; el resto directo → 1
        self.assertEqual(d1['puntaje'], 3 + 1 + 1 + 3 + 1)

    def test_d7_item_29_no_se_invierte_item_30_si(self):
        """D7-P1 (ítem 29) NO debe invertirse; D7-P2 (ítem 30) sí."""
        result = self._resultado([
            ('D7', 'Cambios', [(1, 1), (2, 2)]),
        ])
        d7 = next(d for d in result['dominios'] if d['dominio_clave'] == 'D7')
        # valor=1: item29 directo → 1; item30 invertido → 4-1=3
        self.assertEqual(d7['puntaje'], 1 + 3)

    def test_d5_se_divide_en_dos_dominios_oficiales(self):
        """D5 P1-P2 → 'Jornada de trabajo'; P3-P4 → 'Interferencia trabajo-familia'."""
        result = self._resultado([
            ('D5', 'Jornada', [(1, 1), (2, 2), (3, 3), (4, 4)]),
        ])
        oficiales = {d['nombre']: d for d in result['dominios_oficiales']}
        jornada = oficiales['Jornada de trabajo']
        interferencia = oficiales['Interferencia en la relación trabajo-familia']
        self.assertEqual(jornada['puntaje'], 2)       # P1, P2 con valor=1 cada una
        self.assertEqual(jornada['puntaje_max'], 8)
        self.assertEqual(interferencia['puntaje'], 2)  # P3, P4 con valor=1 cada una
        self.assertEqual(interferencia['puntaje_max'], 8)

    @patch('m06_results.scoring._GUIA_III_INVERSOS', set())
    def test_d13_y_d14_se_funden_en_carga_y_relaciones(self):
        """D13 suma a 'Carga de trabajo'; D14 a 'Relaciones en el trabajo'.
        Inversión desactivada aquí: lo que se ejercita es la fusión de
        dominios (Tabla 6), no la tabla de inversión (ver TestInversion*)."""
        result = self._resultado([
            ('D2', 'Ritmo', [(10, 1), (11, 2), (12, 3)]),
            ('D13', 'Clientes', [(20, 1), (21, 2)]),
            ('D10', 'Companeros', [(30, 1)]),
            ('D14', 'Supervisados', [(40, 1)]),
        ])
        oficiales = {d['nombre']: d for d in result['dominios_oficiales']}
        # Carga de trabajo = D2 (3 items, valor=1) + D13 (2 items, valor=1) = 5
        self.assertEqual(oficiales['Carga de trabajo']['puntaje'], 5)
        # Relaciones en el trabajo = D10 (1 item) + D14 (1 item) = 2
        self.assertEqual(oficiales['Relaciones en el trabajo']['puntaje'], 2)

    def test_dominios_oficiales_cubre_los_10_con_categoria_consistente(self):
        result = self._resultado([('D1', 'Ambiente', [(1, 1)])])
        nombres = {d['nombre'] for d in result['dominios_oficiales']}
        from .scoring import _DOMINIOS_OFICIALES, _CORTES_DOMINIO
        self.assertEqual(nombres, set(_DOMINIOS_OFICIALES))
        for d in result['dominios_oficiales']:
            self.assertEqual(
                d['categoria'],
                _categoria_por_rangos(d['puntaje'], _CORTES_DOMINIO[d['nombre']]),
            )


# ---------------------------------------------------------------------------
# Tests — calcular_resultado (punto de entrada público)
# ---------------------------------------------------------------------------

class TestCalcularResultado(TestCase):

    def test_guia_v_retorna_none(self):
        app = MagicMock()
        app.cuestionario.clave = 'V'
        app.respuestas.all.return_value = []
        self.assertIsNone(calcular_resultado(app))

    def test_guia_i_retorna_dict(self):
        app = MagicMock()
        app.cuestionario.clave = 'I'
        app.respuestas.all.return_value = []
        app.cuestionario.dominios.prefetch_related.return_value.all.return_value = []
        result = calcular_resultado(app)
        self.assertIsNotNone(result)
        self.assertIn('requiere_atencion', result)

    def test_guia_iii_retorna_dict(self):
        app = MagicMock()
        app.cuestionario.clave = 'III'
        app.respuestas.all.return_value = []
        app.cuestionario.dominios.prefetch_related.return_value.all.return_value = []
        result = calcular_resultado(app)
        self.assertIsNotNone(result)
        self.assertIn('categoria', result)
