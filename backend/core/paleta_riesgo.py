"""Codificación visual de los niveles de riesgo de la NOM-035.

Fuente ÚNICA de la paleta oficial (azul claro → verde → amarillo → ámbar →
rojo): la consumen el informe DOCX, sus gráficas y las matrices exportadas a
Excel, de modo que un mismo nivel se vea igual en todos los entregables.

El rojo de la norma aparece rasterizado como #FE0000; aquí se normaliza a
#FF0000.
"""

# Sin '#': el formato que piden openpyxl y el XML de DOCX. Para CSS/matplotlib
# usar `con_gato()`.
NIVEL_COLOR = {
    'nulo':     '9CE5F6',
    'bajo':     '6BF56E',
    'medio':    'FFFF00',
    'alto':     'FFC000',
    'muy_alto': 'FF0000',
}

# Un cuestionario sin clasificar NO es un nivel de riesgo: gris neutro, fuera
# de la escala de la norma.
COLOR_SIN_CALIFICAR = '94A3B8'

NIVEL_LABEL = {
    'nulo':     'Nulo',
    'bajo':     'Bajo',
    'medio':    'Medio',
    'alto':     'Alto',
    'muy_alto': 'Muy alto',
}

DIST_KEYS = ('nulo', 'bajo', 'medio', 'alto', 'muy_alto')


def con_gato(clave):
    """Color del nivel en formato CSS/matplotlib (#RRGGBB)."""
    return '#' + NIVEL_COLOR[clave]


def luminancia_relativa(hex6):
    """Luminancia relativa WCAG 2.1 de un color 'RRGGBB'."""
    canales = [int(hex6[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lineal = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in canales]
    return 0.2126 * lineal[0] + 0.7152 * lineal[1] + 0.0722 * lineal[2]


def texto_contrastante(hex6):
    """'000000' o 'FFFFFF', el que tenga mayor contraste sobre `hex6`
    (WCAG 2.1). Con esta paleta los cinco niveles piden texto negro."""
    luminancia = luminancia_relativa(hex6)
    contraste_negro = (luminancia + 0.05) / 0.05
    contraste_blanco = 1.05 / (luminancia + 0.05)
    return '000000' if contraste_negro >= contraste_blanco else 'FFFFFF'
