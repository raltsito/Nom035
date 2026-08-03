"""Paleta y helpers de estilo openpyxl compartidos por los exports a Excel
del proyecto (muestra NOM-035, respuestas por trabajador, etc.)."""
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

# ── Paleta ────────────────────────────────────────────────────────────────────
ACCENT  = '03C4CE'   # teal principal
NAVY    = '0A2540'   # azul oscuro para títulos
LIGHT   = 'E8FAFB'   # fondo alterno claro
WHITE   = 'FFFFFF'
GRAY    = 'F4F6F8'   # fondo headers de estrato
SUBHEAD = '64748B'   # texto gris medio


# Paleta de la interfaz web (variables --nom-riesgo-* del frontend). La usan
# los exports que acompañan a una vista de la plataforma, como la matriz de
# Guía I. Para la codificación visual de la NOM-035 ver `core.paleta_riesgo`.
RIESGO = {
    'nulo':          '10B981',
    'bajo':          '84CC16',
    'medio':         'F59E0B',
    'alto':          'EF4444',
    'muy_alto':      '7C3AED',
    'sin_calificar': '94A3B8',
}


def fill(hex_color):
    return PatternFill('solid', fgColor=hex_color)


def font(bold=False, color=NAVY, size=10):
    return Font(bold=bold, color=color, name='Calibri', size=size)


def border():
    s = Side(style='thin', color='DDE1E7')
    return Border(left=s, right=s, top=s, bottom=s)


def center(wrap=False):
    return Alignment(horizontal='center', vertical='center', wrap_text=wrap)


def left(wrap=False):
    return Alignment(horizontal='left', vertical='center', wrap_text=wrap)
