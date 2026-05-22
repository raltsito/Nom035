from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

W, H = A4

NUEVO_URL  = "https://www.nom.intra.org.mx/login"
REMITENTE  = "Carlos Gonzalez"
OUTPUT     = r"C:\Users\carlo\Downloads\LEAR\aviso_nuevo_link.pdf"


def esc(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def ps(name, **kw):
    return ParagraphStyle(name, **kw)

def generar():
    NAVY    = colors.HexColor("#0f172a")
    BLUE    = colors.HexColor("#1e40af")
    BLUE_L  = colors.HexColor("#dbeafe")
    AMBER   = colors.HexColor("#d97706")
    AMBER_L = colors.HexColor("#fef3c7")
    GRAY    = colors.HexColor("#64748b")
    LGRAY   = colors.HexColor("#f8fafc")
    BORDER  = colors.HexColor("#e2e8f0")
    GREEN_L = colors.HexColor("#dcfce7")
    GREEN_B = colors.HexColor("#86efac")
    GREEN_T = colors.HexColor("#166534")
    GREEN_I = colors.HexColor("#16a34a")

    doc = SimpleDocTemplate(
        OUTPUT,
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
        Paragraph('<font color="#93c5fd" size="8">Actualización de acceso</font>',
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
    story.append(Spacer(1, 5*mm))

    # ── SALUDO ────────────────────────────────────────────────────────────────
    story.append(Paragraph("Estimado usuario,",
        ps("sal", fontName="Helvetica-Bold", fontSize=12, leading=16, textColor=NAVY, spaceAfter=3)))
    story.append(Paragraph(
        "Nos dirigimos a usted con la finalidad de informarle sobre un cambio importante en el acceso "
        "a la plataforma <b>NOM-035-STPS-2018</b>. Hemos detectado que el enlace de acceso que le fue "
        "proporcionado anteriormente ha presentado intermitencia e inconvenientes técnicos que han dificultado "
        "el ingreso a la plataforma.",
        ps("body", fontName="Helvetica", fontSize=9.5, leading=15, textColor=NAVY)))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        "Con el objetivo de garantizar una experiencia de acceso estable y sin interrupciones, "
        "hemos habilitado una nueva dirección de acceso.",
        ps("body2", fontName="Helvetica", fontSize=9.5, leading=15, textColor=NAVY)))
    story.append(Spacer(1, 5*mm))

    # ── NUEVO ACCESO ──────────────────────────────────────────────────────────
    story.append(Paragraph("NUEVO ENLACE DE ACCESO", ps("sec", fontName="Helvetica-Bold",
        fontSize=7.5, leading=10, textColor=GRAY, letterSpacing=1.0)))
    story.append(Spacer(1, 1.5*mm))

    url_table = Table([
        [Paragraph("URL de acceso", ps("sl", fontName="Helvetica", fontSize=8.5, leading=12, textColor=GRAY)),
         Paragraph(f'<font color="#1e40af"><b>{esc(NUEVO_URL)}</b></font>',
                   ps("url", fontName="Helvetica-Bold", fontSize=10.5, leading=13, textColor=BLUE))],
    ], colWidths=[32*mm, CW-32*mm])
    url_table.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), LGRAY),
        ("BOX",           (0,0), (-1,-1), 0.8, BORDER),
        ("TOPPADDING",    (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ("LEFTPADDING",   (0,0), (-1,-1), 12),
        ("RIGHTPADDING",  (-1,0),(-1,-1), 12),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(url_table)
    story.append(Spacer(1, 4*mm))

    # ── AVISO POSITIVO ────────────────────────────────────────────────────────
    aviso = Table([[
        Paragraph("✓", ps("avi", fontName="Helvetica-Bold", fontSize=13, leading=15, textColor=GREEN_I)),
        Paragraph(
            "<b>Sus credenciales de acceso (usuario y contraseña) permanecen sin cambios.</b> "
            "Únicamente es necesario actualizar la dirección web (URL) que utiliza para ingresar a la plataforma.",
            ps("avt", fontName="Helvetica", fontSize=9, leading=13, textColor=GREEN_T)),
    ]], colWidths=[9*mm, CW-9*mm])
    aviso.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), GREEN_L),
        ("BOX",           (0,0), (-1,-1), 0.8, GREEN_B),
        ("TOPPADDING",    (0,0), (-1,-1), 9),
        ("BOTTOMPADDING", (0,0), (-1,-1), 9),
        ("LEFTPADDING",   (0,0), (0,-1),  10),
        ("LEFTPADDING",   (1,0), (1,-1),  8),
        ("RIGHTPADDING",  (-1,0),(-1,-1), 12),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(aviso)
    story.append(Spacer(1, 4*mm))

    # ── NOTA AMBER ────────────────────────────────────────────────────────────
    nota = Table([[
        Paragraph("!", ps("ico", fontName="Helvetica-Bold", fontSize=13, leading=15, textColor=AMBER)),
        Paragraph(
            "<b>Enlace anterior inhabilitado —</b> "
            "Le informamos que el enlace previo dejará de estar disponible en los próximos días. "
            "Le recomendamos actualizar sus favoritos o marcadores con la nueva dirección a la brevedad posible "
            "para evitar cualquier interrupción en el uso de la plataforma.",
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
    story.append(Spacer(1, 6*mm))

    # ── FIRMA ─────────────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER))
    story.append(Spacer(1, 3.5*mm))
    story.append(Paragraph(
        "Lamentamos los inconvenientes que el problema con el enlace anterior pudo haberle ocasionado. "
        "Quedamos a su disposición para cualquier duda o aclaración.",
        ps("body3", fontName="Helvetica", fontSize=9.5, leading=14, textColor=NAVY)))
    story.append(Spacer(1, 2.5*mm))
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
    print(f"PDF generado: {OUTPUT}")


generar()
