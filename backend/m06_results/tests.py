from unittest.mock import MagicMock, patch
from django.test import TestCase

from .scoring import (
    calcular_resultado,
    _calcular_guia_i,
    _calcular_guia_iii,
    _categoria_por_rangos,
    GUIA_III_GLOBAL,
    GUIA_III_DOMINIOS,
)


# ---------------------------------------------------------------------------
# Helpers para construir mocks de Aplicacion
# ---------------------------------------------------------------------------

def _pregunta(id, tipo='frecuencia', inversa=False):
    p = MagicMock()
    p.id             = id
    p.tipo_respuesta = tipo
    p.inversa        = inversa
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
        self.assertEqual(_categoria_por_rangos(0, GUIA_III_GLOBAL), 'nulo')
        self.assertEqual(_categoria_por_rangos(19, GUIA_III_GLOBAL), 'nulo')

    def test_bajo(self):
        self.assertEqual(_categoria_por_rangos(20, GUIA_III_GLOBAL), 'bajo')
        self.assertEqual(_categoria_por_rangos(44, GUIA_III_GLOBAL), 'bajo')

    def test_medio(self):
        self.assertEqual(_categoria_por_rangos(45, GUIA_III_GLOBAL), 'medio')
        self.assertEqual(_categoria_por_rangos(79, GUIA_III_GLOBAL), 'medio')

    def test_alto(self):
        self.assertEqual(_categoria_por_rangos(80, GUIA_III_GLOBAL), 'alto')
        self.assertEqual(_categoria_por_rangos(140, GUIA_III_GLOBAL), 'alto')

    def test_muy_alto(self):
        self.assertEqual(_categoria_por_rangos(141, GUIA_III_GLOBAL), 'muy_alto')
        self.assertEqual(_categoria_por_rangos(999, GUIA_III_GLOBAL), 'muy_alto')


# ---------------------------------------------------------------------------
# Tests — Guía I
# ---------------------------------------------------------------------------

class TestGuiaI(TestCase):

    def _app_con_respuestas(self, d1_positivos, sintomas_positivos):
        """
        Construye aplicación Guía I y respuestas.
        d1_positivos: cuántas preguntas de D1 marcan "Sí".
        sintomas_positivos: cuántos "Sí" en D2+D3+D4 combinados.
        """
        # D1: 6 preguntas si_no
        d1_preguntas = [_pregunta(i, 'si_no') for i in range(1, 7)]
        # D2-D4: 14 preguntas si_no en total (simplificado)
        d2_preguntas = [_pregunta(i, 'si_no') for i in range(7, 14)]

        dominios = [
            _dominio('D1', 'ATS', d1_preguntas),
            _dominio('D2', 'Síntomas', d2_preguntas),
        ]

        app = MagicMock()
        app.cuestionario.clave = 'I'
        app.cuestionario.dominios.prefetch_related.return_value.all.return_value = dominios

        respuestas = {}
        for i, p in enumerate(d1_preguntas):
            respuestas[p.id] = _respuesta(1 if i < d1_positivos else 0)
        for i, p in enumerate(d2_preguntas):
            respuestas[p.id] = _respuesta(1 if i < sintomas_positivos else 0)

        app.respuestas.all.return_value = [
            MagicMock(pregunta_id=pid, valor=r.valor)
            for pid, r in respuestas.items()
        ]
        return app, respuestas

    def test_caso_positivo(self):
        """D1 ≥ 1 Y síntomas ≥ 2 → requiere_atencion=True."""
        app, respuestas = self._app_con_respuestas(d1_positivos=1, sintomas_positivos=2)
        result = _calcular_guia_i(app, respuestas)
        self.assertTrue(result['requiere_atencion'])
        self.assertEqual(result['categoria'], 'requiere_atencion')

    def test_solo_un_sintoma(self):
        """D1 ≥ 1 pero solo 1 síntoma → requiere_atencion=False."""
        app, respuestas = self._app_con_respuestas(d1_positivos=1, sintomas_positivos=1)
        result = _calcular_guia_i(app, respuestas)
        self.assertFalse(result['requiere_atencion'])
        self.assertEqual(result['categoria'], 'sin_indicadores')

    def test_d1_negativo(self):
        """Sin acontecimiento en D1 → requiere_atencion=False aunque haya síntomas."""
        app, respuestas = self._app_con_respuestas(d1_positivos=0, sintomas_positivos=5)
        result = _calcular_guia_i(app, respuestas)
        self.assertFalse(result['requiere_atencion'])
        self.assertEqual(result['categoria'], 'sin_indicadores')

    def test_sin_respuestas(self):
        """Trabajador que no respondió nada → sin_indicadores."""
        app, respuestas = self._app_con_respuestas(d1_positivos=0, sintomas_positivos=0)
        result = _calcular_guia_i(app, respuestas)
        self.assertFalse(result['requiere_atencion'])
        self.assertEqual(result['categoria'], 'sin_indicadores')

    def test_umbral_exacto_dos_sintomas(self):
        """Exactamente 2 síntomas con D1 positivo → requiere_atencion=True."""
        app, respuestas = self._app_con_respuestas(d1_positivos=2, sintomas_positivos=2)
        result = _calcular_guia_i(app, respuestas)
        self.assertTrue(result['requiere_atencion'])


# ---------------------------------------------------------------------------
# Tests — Guía III
# ---------------------------------------------------------------------------

class TestGuiaIII(TestCase):

    def _app_puntaje(self, puntaje_deseado):
        """
        Crea una aplicación Guía III con un solo dominio D1 y respuestas
        ajustadas para alcanzar el puntaje_deseado.
        Usa preguntas directas (no inversas) con valor = 4 cada una.
        """
        n_preguntas = max(1, (puntaje_deseado + 3) // 4)
        preguntas   = [_pregunta(i, 'frecuencia', False) for i in range(1, n_preguntas + 1)]

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

    def test_nivel_nulo(self):
        app, respuestas = self._app_puntaje(10)
        result = _calcular_guia_iii(app, respuestas)
        self.assertEqual(result['categoria'], 'nulo')
        self.assertIsNone(result['requiere_atencion'])

    def test_nivel_bajo(self):
        app, respuestas = self._app_puntaje(30)
        result = _calcular_guia_iii(app, respuestas)
        self.assertEqual(result['categoria'], 'bajo')

    def test_nivel_medio(self):
        app, respuestas = self._app_puntaje(60)
        result = _calcular_guia_iii(app, respuestas)
        self.assertEqual(result['categoria'], 'medio')

    def test_nivel_alto(self):
        app, respuestas = self._app_puntaje(100)
        result = _calcular_guia_iii(app, respuestas)
        self.assertEqual(result['categoria'], 'alto')

    def test_nivel_muy_alto(self):
        app, respuestas = self._app_puntaje(150)
        result = _calcular_guia_iii(app, respuestas)
        self.assertEqual(result['categoria'], 'muy_alto')

    def test_d13_excluido_si_no_aplica(self):
        """D13 con filtro respondido 'No' no suma al puntaje total."""
        filtro  = _pregunta(100, 'si_no')
        p65     = _pregunta(101, 'frecuencia')
        p66     = _pregunta(102, 'frecuencia')
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
        filtro = _pregunta(100, 'si_no')
        p65    = _pregunta(101, 'frecuencia')
        p66    = _pregunta(102, 'frecuencia')
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
