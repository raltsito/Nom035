"""Gráficas (matplotlib) embebidas en el Informe Diagnóstico NOM-035 (DOCX).

Funciones puras: reciben etiquetas/valores ya agregados y devuelven un PNG en
BytesIO listo para `doc.add_picture(...)`. No consultan la base de datos ni
conocen tenant/ciclo — todo el cálculo vive en `views.py`.
"""
import io

import matplotlib
matplotlib.use('Agg')
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np

from core import paleta_riesgo as paleta

# Codificación visual de la NOM-035: definida una sola vez en
# core.paleta_riesgo y compartida con el DOCX y los Excel.
NIVEL_COLOR = {clave: paleta.con_gato(clave) for clave in paleta.DIST_KEYS}
NIVEL_LABEL = dict(paleta.NIVEL_LABEL)
DIST_KEYS = paleta.DIST_KEYS

_CHART_COLORS = ['#C8102E', '#1A1A2E', '#555555', '#888888',
                  '#AAAAAA', '#BBBBBB', '#CCCCCC', '#DDDDDD']


def chart_pie(labels, values):
    """Pastel 3D: cara superior elíptica + paredes laterales extruidas."""
    total = sum(values)
    if total == 0:
        return io.BytesIO()
    fracs = [v / total for v in values]
    cols = _CHART_COLORS[:len(values)]

    DEPTH = 0.14
    YSCALE = 0.48

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-0.85 - DEPTH, 0.75)
    ax.set_aspect('equal')
    ax.axis('off')
    fig.patch.set_facecolor('white')

    starts = [np.pi / 2]
    for f in fracs:
        starts.append(starts[-1] - 2 * np.pi * f)
    mids = [(starts[i] + starts[i + 1]) / 2 for i in range(len(fracs))]

    def arc(a1, a2):
        t = np.linspace(a1, a2, max(60, int(abs(a2 - a1) / (2 * np.pi) * 200)))
        return np.cos(t), np.sin(t) * YSCALE

    # Paredes laterales (back→front por ángulo medio)
    order = sorted(range(len(fracs)), key=lambda i: np.sin(mids[i]))
    for i in order:
        cx, cy = arc(starts[i], starts[i + 1])
        rgb = mcolors.to_rgb(cols[i])
        dark = tuple(max(0, c * 0.55) for c in rgb)
        wall_x = np.concatenate([[0], cx, [0]])
        wall_yt = np.concatenate([[0], cy, [0]])
        wall_yb = wall_yt - DEPTH
        poly_x = np.concatenate([wall_x, wall_x[::-1]])
        poly_y = np.concatenate([wall_yt, wall_yb[::-1]])
        ax.fill(poly_x, poly_y, color=dark, zorder=2, linewidth=0)

    # Cara superior
    for i in range(len(fracs)):
        cx, cy = arc(starts[i], starts[i + 1])
        px = np.concatenate([[0], cx, [0]])
        py = np.concatenate([[0], cy, [0]])
        ax.fill(px, py, color=cols[i], zorder=5, linewidth=0.7, edgecolor='white')

        pct = fracs[i] * 100
        if pct >= 4:
            lx = 0.60 * np.cos(mids[i])
            ly = 0.60 * np.sin(mids[i]) * YSCALE
            ax.text(lx, ly, f'{pct:.1f}%', ha='center', va='center',
                    fontsize=8.5, fontweight='bold', color='white', zorder=7)

    handles = [mpatches.Patch(facecolor=cols[i], label=f'{labels[i]}  (n={values[i]})')
               for i in range(len(labels))]
    ax.legend(handles=handles, loc='lower center', bbox_to_anchor=(0.5, 0.0),
              fontsize=8, frameon=False, ncol=min(2, len(labels)))

    plt.tight_layout()
    bio = io.BytesIO()
    plt.savefig(bio, format='png', dpi=140, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    bio.seek(0)
    return bio


def chart_barh(labels, pcts, ns):
    """Barras horizontales 3D: cara frontal + cara superior + tapa derecha."""
    BASE = '#C8102E'
    DX = 0.018
    DY = 0.22
    BH = 0.50
    n = len(labels)

    fig, ax = plt.subplots(figsize=(7, max(2.4, n * 0.65 + 0.8)))
    ax.axis('off')
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.6, n - 0.1 + DY + 0.3)
    fig.patch.set_facecolor('white')

    max_pct = max(pcts + [1])
    SCALE = 0.72
    depth_x = SCALE * DX * 6

    rgb = mcolors.to_rgb(BASE)
    light = tuple(min(1.0, c * 1.45 + 0.1) for c in rgb)
    dark = tuple(max(0.0, c * 0.60) for c in rgb)

    for i, (lbl, pct, ni) in enumerate(zip(labels[::-1], pcts[::-1], ns[::-1])):
        w = (pct / max_pct) * SCALE
        y = i
        y0, y1 = y - BH / 2, y + BH / 2

        ax.fill([0, w, w, 0], [y0, y0, y1, y1],
                color=BASE, linewidth=0.5, edgecolor='white', zorder=3)
        ax.fill([0, w, w + depth_x, depth_x],
                [y1, y1, y1 + DY, y1 + DY],
                color=light, linewidth=0.5, edgecolor='white', zorder=4)
        ax.fill([w, w + depth_x, w + depth_x, w],
                [y0, y0 + DY, y1 + DY, y1],
                color=dark, linewidth=0.5, edgecolor='white', zorder=4)
        ax.text(w + depth_x + 0.015, y + DY / 2,
                f'{pct:.1f}%  (n={ni})', va='center', fontsize=7.5, color='#1A1A2E')
        ax.text(-0.01, y, lbl, ha='right', va='center', fontsize=8, color='#1A1A2E')

    xtick_step = max(5, round(max_pct / 5 / 5) * 5)
    xtick_vals = np.arange(0, max_pct + 1, xtick_step)
    ax.set_xticks([v / max_pct * SCALE for v in xtick_vals])
    ax.set_xticklabels([f'{v:.0f}%' for v in xtick_vals], fontsize=7.5)
    ax.tick_params(axis='x', bottom=True, labelbottom=True)
    ax.spines['bottom'].set_visible(True)
    ax.spines['bottom'].set_position(('data', -0.55))

    plt.tight_layout()
    bio = io.BytesIO()
    plt.savefig(bio, format='png', dpi=140, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    bio.seek(0)
    return bio


def chart_nivel_dist(nombre, dist, n):
    """Barras horizontales 3D coloreadas por nivel de riesgo NOM-035."""
    niveles = list(DIST_KEYS)
    labels = [NIVEL_LABEL[k] for k in niveles]
    counts = [dist[k] for k in niveles]
    pcts = [c / n * 100 if n else 0 for c in counts]
    hex_cols = [NIVEL_COLOR[k] for k in niveles]

    DX = 0.015
    DY = 0.20
    BH = 0.46
    max_pct = max(pcts + [1])
    SCALE = 0.58
    depth_x = SCALE * DX * 8

    fig, ax = plt.subplots(figsize=(5.8, 2.9))
    ax.axis('off')
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.6, len(niveles) - 0.1 + DY + 0.3)
    fig.patch.set_facecolor('white')

    for i, (lbl, pct, cnt, hcol) in enumerate(
            zip(labels[::-1], pcts[::-1], counts[::-1], hex_cols[::-1])):
        w = (pct / max_pct) * SCALE
        y = i
        y0, y1 = y - BH / 2, y + BH / 2
        rgb = mcolors.to_rgb(hcol)
        light = tuple(min(1.0, c * 1.4 + 0.1) for c in rgb)
        dark = tuple(max(0.0, c * 0.55) for c in rgb)
        ax.fill([0, w, w, 0], [y0, y0, y1, y1],
                color=hcol, linewidth=0.4, edgecolor='white', zorder=3)
        ax.fill([0, w, w + depth_x, depth_x], [y1, y1, y1 + DY, y1 + DY],
                color=light, linewidth=0.4, edgecolor='white', zorder=4)
        ax.fill([w, w + depth_x, w + depth_x, w], [y0, y0 + DY, y1 + DY, y1],
                color=dark, linewidth=0.4, edgecolor='white', zorder=4)
        ax.text(w + depth_x + 0.01, y + DY / 2,
                f'{pct:.1f}%  (n={cnt})', va='center', fontsize=7, color='#1A1A2E')
        ax.text(-0.01, y, lbl, ha='right', va='center', fontsize=7.5, color='#1A1A2E')

    ax.set_title(nombre, fontsize=8, color='#1A1A2E', fontweight='bold', pad=5)
    plt.tight_layout()
    bio = io.BytesIO()
    plt.savefig(bio, format='png', dpi=130, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    bio.seek(0)
    return bio


def chart_ats(filas):
    """Barras agrupadas H/M por pregunta de Guía I, mostrando % Sí.

    `filas`: lista de dicts con `orden`, `h_si`, `h_no`, `m_si`, `m_no`.
    """
    n = len(filas)
    labels = [f'P{f["orden"]}' for f in filas]
    h_totales = [f['h_si'] + f['h_no'] for f in filas]
    m_totales = [f['m_si'] + f['m_no'] for f in filas]
    h_pct = [f['h_si'] / t * 100 if t else 0 for f, t in zip(filas, h_totales)]
    m_pct = [f['m_si'] / t * 100 if t else 0 for f, t in zip(filas, m_totales)]

    x = np.arange(n)
    BW = 0.32
    DX, DY = 0.06, 4.0

    fig, ax = plt.subplots(figsize=(max(5, n * 0.9 + 1.5), 4))
    fig.patch.set_facecolor('white')

    def bar3d(positions, heights, color, offset=0):
        rgb = mcolors.to_rgb(color)
        light = tuple(min(1, c * 1.4 + 0.08) for c in rgb)
        dark = tuple(max(0, c * 0.55) for c in rgb)
        for xi, h in zip(positions, heights):
            x0, x1 = xi + offset, xi + offset + BW
            ax.fill([x0, x1, x1, x0], [0, 0, h, h], color=color, linewidth=0.5, edgecolor='white', zorder=3)
            ax.fill([x0, x1, x1 + DX, x0 + DX], [h, h, h + DY, h + DY], color=light, linewidth=0.5, edgecolor='white', zorder=4)
            ax.fill([x1, x1 + DX, x1 + DX, x1], [0, DY, h + DY, h], color=dark, linewidth=0.5, edgecolor='white', zorder=4)
            if h > 0:
                ax.text(xi + offset + BW / 2, h + DY + 1, f'{h:.1f}%', ha='center', fontsize=7, color='#1A1A2E', zorder=5)

    bar3d(x, h_pct, '#C8102E', offset=0)
    bar3d(x, m_pct, '#1A1A2E', offset=BW + 0.04)

    ax.set_xticks(x + BW / 2 + 0.02)
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel('% Sí', fontsize=8)
    ax.set_ylim(0, max(max(h_pct + m_pct, default=0) + DY + 12, 20))
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.legend(handles=[mpatches.Patch(color='#C8102E', label='Hombres'),
                        mpatches.Patch(color='#1A1A2E', label='Mujeres')],
              fontsize=8, frameon=False)
    plt.tight_layout()
    bio = io.BytesIO()
    plt.savefig(bio, format='png', dpi=140, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    bio.seek(0)
    return bio
