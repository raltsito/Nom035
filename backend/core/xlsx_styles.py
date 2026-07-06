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
