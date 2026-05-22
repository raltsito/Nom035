from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
import os
import re

W, H = A4

URL       = "https://www.nom035.collaboracali.com/login"
REMITENTE = "Carlos Gonzalez"
DEST      = r"C:\Users\carlo\Downloads\LEAR\doc bienvenida"

PLANTAS = [
    ("Piedras Negras I & II", "pnegras12",  "PN12#Co4h_25!"),
    ("Piedras Negras III",    "pnegras3",   "PN3$C0ah_25!"),
    ("Piedras Negras IV",     "pnegras4",   "PN4&C04h_25!"),
    ("San Luis",              "sanluis",    "SL#P0t0s1_25!"),
    ("Puebla",                "puebla",     "Pu3@M3x_25!"),
    ("Hermosillo",            "hermosillo", "H3r#S0n0r4_25!"),
    ("Planta 726 Ramos",      "ramos726",   "R726$NL_25!x"),
    ("Naucalpan",             "naucalpan",  "N4u@EdoMx_25!"),
    ("Reynosa",               "reynosa",    "R3y#T4mp_25!"),
    ("Silao",                 "silao",      "S!l4o@Gt0_25!"),
    ("Toluca",                "toluca",     "T0l#EdoMx_25!"),
    ("Saltillo",              "saltillo",   "S4lt@C04h_25!"),
    ("Zapotitlan",            "zapotitlan", "Z4p0@CDMX_25!"),
    ("Arteaga",               "arteaga",   "Art3@C04h_25!"),
]

def esc(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def ps(name, **kw):
    return ParagraphStyle(name, **kw)

def generar(tenant, usuario, password, output):
    NAVY   = colors.HexColor("#0f172a")
    BLUE   = colors.HexColor("#1e40af")
    BLUE_L = colors.HexColor("#dbeafe")
    AMBER  = colors.HexColor("#d97706")
    AMBER_L= colors.HexColor("#fef3c7")
    GRAY   = colors.HexColor("#64748b")
    LGRAY  = colors.HexColor("#f8fafc")
    BORDER = colors.HexColor("#e2e8f0")
    RED_L  = colors.HexColor("#fee2e2")
    RED_B  = colors.HexColor("#fca5a5")
    RED_T  = colors.HexColor("#991b1b")
    RED_I  = colors.HexColor("#dc2626")

    doc = SimpleDocTemplate(
        output,
        pagesize=A4,
        leftMargin=20*mm, rightMargin=20*mm,
        topMargin=14*mm, bottomMargin=14*mm,
    )

    CW = W - 40*mm
    story = []

    # ── HEADER ────────────────────────────────────────────────────────────────
    hdr = Table([[
        Paragraph('<font color="#ffffff" size="15"><b>NOM-035-STPS-2018</b></font><br/>'
                  '<font color="#93c5fd" size="8">Plataforma de Cumplimiento</font>',
                  ps("h1", fontName="Helvetica-Bold", fontSize=15, leading=20, textColor=colors.white)),
        Paragraph('<font color="#93c5fd" size="8">Acceso a la plataforma</font>',
                  ps("h2", fontName="Helvetica", fontSize=8, leading=12,
                     textColor=colors.HexColor("#93c5fd"), alignment=TA_RIGHT)),
    ]], colWidths=[CW*0.65, CW*0.35])
    hdr.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), NAVY),
        ("TOPPADDING",    (0,0), (-1,-1), 14),
        ("BOTTOMPADDING", (0,0), (-1,-1), 14),
        ("LEFTPADDING",   (0,0), (0,-1),  18),
        ("RIGHTPADDING",  (-1,0),(-1,-1), 18),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(hdr)
    story.append(Spacer(1, 4*mm))

    # ── SALUDO ────────────────────────────────────────────────────────────────
    story.append(Paragraph("Hola,", ps("sal", fontName="Helvetica-Bold",
        fontSize=12, leading=16, textColor=NAVY, spaceAfter=3)))
    story.append(Paragraph(
        "Nos da gusto informarte que tu acceso a la plataforma <b>NOM-035-STPS-2018</b> ya está listo. "
        "A continuación encontrarás tus credenciales y una breve descripción de lo que puedes hacer dentro.",
        ps("body", fontName="Helvetica", fontSize=9.5, leading=14, textColor=NAVY)))
    story.append(Spacer(1, 4*mm))

    # ── CREDENCIALES ──────────────────────────────────────────────────────────
    story.append(Paragraph("ACCESO", ps("sec", fontName="Helvetica-Bold",
        fontSize=7.5, leading=10, textColor=GRAY, letterSpacing=1.0)))
    story.append(Spacer(1, 1.5*mm))

    cred_table = Table([
        [Paragraph("URL de acceso", ps("sl", fontName="Helvetica", fontSize=8.5, leading=12, textColor=GRAY)),
         Paragraph(f'<font color="#1e40af"><b>{esc(URL)}</b></font>',
                   ps("url", fontName="Helvetica-Bold", fontSize=9.5, leading=13, textColor=BLUE))],
        [Paragraph("Usuario", ps("sl2", fontName="Helvetica", fontSize=8.5, leading=12, textColor=GRAY)),
         Paragraph(f"<b>{esc(usuario)}</b>",
                   ps("u", fontName="Courier-Bold", fontSize=10.5, leading=13, textColor=NAVY))],
        [Paragraph("Contraseña", ps("sl3", fontName="Helvetica", fontSize=8.5, leading=12, textColor=GRAY)),
         Paragraph(f"<b>{esc(password)}</b>",
                   ps("p", fontName="Courier-Bold", fontSize=10.5, leading=13,
                      textColor=colors.HexColor("#92400e")))],
    ], colWidths=[32*mm, CW-32*mm])
    cred_table.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), LGRAY),
        ("BACKGROUND",    (0,2), (-1,2),  AMBER_L),
        ("BOX",           (0,0), (-1,-1), 0.8, BORDER),
        ("LINEBELOW",     (0,0), (-1,-2), 0.5, BORDER),
        ("TOPPADDING",    (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ("LEFTPADDING",   (0,0), (-1,-1), 12),
        ("RIGHTPADDING",  (-1,0),(-1,-1), 12),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(cred_table)
    story.append(Spacer(1, 4*mm))

    # ── SECCIONES ─────────────────────────────────────────────────────────────
    story.append(Paragraph("¿QUÉ ENCONTRARÁS DENTRO?", ps("sec2", fontName="Helvetica-Bold",
        fontSize=7.5, leading=10, textColor=GRAY, letterSpacing=1.0)))
    story.append(Spacer(1, 1.5*mm))

    tabs = [
        ("TRABAJADORES",  "Consulta y gestiona el directorio de colaboradores registrados en tu empresa."),
        ("CUESTIONARIOS", "Accede a los cuestionarios NOM-035 asignados y monitorea su avance de aplicación."),
        ("RESULTADOS",    "Visualiza los resultados por trabajador y área una vez contestados los cuestionarios."),
        ("CALCULADORA",   "Determina a qué trabajadores se les aplicará cada cuestionario, calculado mediante las fórmulas establecidas por la norma."),
        ("DASHBOARD",     "Vista ejecutiva del cumplimiento: avance general, pendientes y resumen por área."),
    ]
    tab_rows = [[
        Paragraph(f'<font color="#1e40af"><b>{t}</b></font>',
                  ps(f"tn{i}", fontName="Helvetica-Bold", fontSize=8, leading=11, textColor=BLUE)),
        Paragraph(d, ps(f"td{i}", fontName="Helvetica", fontSize=9, leading=13, textColor=NAVY)),
    ] for i, (t, d) in enumerate(tabs)]

    tabs_table = Table(tab_rows, colWidths=[30*mm, CW-30*mm])
    tabs_table.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), colors.white),
        ("BACKGROUND",    (0,0), (0,-1),  BLUE_L),
        ("BOX",           (0,0), (-1,-1), 0.8, BORDER),
        ("LINEBELOW",     (0,0), (-1,-2), 0.5, BORDER),
        ("TOPPADDING",    (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ("LEFTPADDING",   (0,0), (0,-1),  9),
        ("LEFTPADDING",   (1,0), (1,-1),  12),
        ("RIGHTPADDING",  (-1,0),(-1,-1), 12),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(tabs_table)
    story.append(Spacer(1, 4*mm))

    # ── AVISO IMPORTANTE ──────────────────────────────────────────────────────
    aviso = Table([[
        Paragraph("!", ps("avi", fontName="Helvetica-Bold", fontSize=14, leading=15, textColor=RED_I)),
        Paragraph(
            "<b>Por favor, no capturen respuestas aún.</b> "
            "Si se registran respuestas en este momento, el trabajador quedará bloqueado "
            "y no podrá contestar los cuestionarios en el futuro.",
            ps("avt", fontName="Helvetica", fontSize=9, leading=13, textColor=RED_T)),
    ]], colWidths=[9*mm, CW-9*mm])
    aviso.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), RED_L),
        ("BOX",           (0,0), (-1,-1), 0.8, RED_B),
        ("TOPPADDING",    (0,0), (-1,-1), 9),
        ("BOTTOMPADDING", (0,0), (-1,-1), 9),
        ("LEFTPADDING",   (0,0), (0,-1),  10),
        ("LEFTPADDING",   (1,0), (1,-1),  8),
        ("RIGHTPADDING",  (-1,0),(-1,-1), 12),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(aviso)
    story.append(Spacer(1, 4*mm))

    # ── NOTA EXCEL ────────────────────────────────────────────────────────────
    nota = Table([[
        Paragraph("?", ps("ico", fontName="Helvetica-Bold", fontSize=13, leading=15, textColor=AMBER)),
        Paragraph(
            "<b>Nota sobre tu base de datos —</b> "
            "Si el Excel que nos enviaste tenía tipos de respuesta incorrectos, no te preocupes. "
            "En cuanto nos hagas llegar el archivo corregido, actualizaremos la información en la plataforma.",
            ps("nt", fontName="Helvetica", fontSize=9, leading=13,
               textColor=colors.HexColor("#92400e"))),
    ]], colWidths=[9*mm, CW-9*mm])
    nota.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), AMBER_L),
        ("BOX",           (0,0), (-1,-1), 0.8, colors.HexColor("#fcd34d")),
        ("TOPPADDING",    (0,0), (-1,-1), 9),
        ("BOTTOMPADDING", (0,0), (-1,-1), 9),
        ("LEFTPADDING",   (0,0), (0,-1),  10),
        ("LEFTPADDING",   (1,0), (1,-1),  8),
        ("RIGHTPADDING",  (-1,0),(-1,-1), 12),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(nota)
    story.append(Spacer(1, 5*mm))

    # ── FIRMA ─────────────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER))
    story.append(Spacer(1, 3.5*mm))
    story.append(Paragraph("Cualquier duda, con gusto te ayudamos.",
        ps("body2", fontName="Helvetica", fontSize=9.5, leading=14, textColor=NAVY)))
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph(f"<b>{REMITENTE}</b>",
        ps("firma", fontName="Helvetica-Bold", fontSize=10, leading=13, textColor=NAVY)))
    story.append(Paragraph("nom035@collaboracali.com",
        ps("cargo", fontName="Helvetica", fontSize=8.5, leading=12, textColor=GRAY)))

    # ── FOOTER ────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 5*mm))
    story.append(Paragraph(
        "Este documento contiene información confidencial. No compartir por canales no seguros.",
        ps("ctr", fontName="Helvetica", fontSize=8, leading=11, textColor=GRAY, alignment=TA_CENTER)))

    doc.build(story)


# ── GENERAR TODOS ─────────────────────────────────────────────────────────────
for tenant, usuario, password in PLANTAS:
    nombre_archivo = re.sub(r'[^a-zA-Z0-9_]', '_', tenant).strip('_')
    output = os.path.join(DEST, f"carta_{nombre_archivo}.pdf")
    generar(tenant, usuario, password, output)
    print(f"  OK  {output}")

print(f"\n{len(PLANTAS)} PDFs generados en {DEST}")
