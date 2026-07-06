"""Generador del borrador DOCX del reporte psicológico NOM-035.

Consume el mismo ctx que produce _build_psico_context() en views.py — nunca
importa interpretaciones.py ni contenido_normativo.py directamente. Esto
garantiza que el borrador y el HTML/PDF final queden idénticos en redacción
y estructura (las 13 secciones del estándar LEAR), sin duplicar lógica de
negocio en dos lugares.
"""
import io

from django.contrib.staticfiles import finders
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

NIVEL_LABEL_DOCX = {
    'nulo': 'Nulo', 'bajo': 'Bajo', 'medio': 'Medio',
    'alto': 'Alto', 'muy_alto': 'Muy alto',
}


def _set_base_styles(doc):
    normal = doc.styles['Normal']
    normal.font.name = 'Calibri'
    normal.font.size = Pt(11)


def _heading(doc, text, level=2):
    doc.add_heading(text, level=level)


def _simple_table(doc, headers, rows):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = 'Table Grid'
    hdr = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = str(h)
        for p in hdr[i].paragraphs:
            for r in p.runs:
                r.bold = True
    for row_vals in rows:
        cells = table.add_row().cells
        for i, v in enumerate(row_vals):
            cells[i].text = str(v)
    doc.add_paragraph()


def _add_portada(doc, ctx):
    titulo = doc.add_paragraph()
    titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = titulo.add_run('BORRADOR — Sujeto a revisión y aprobación profesional')
    run.bold = True
    run.font.color.rgb = RGBColor(0xC0, 0x20, 0x20)
    run.font.size = Pt(12)

    doc.add_heading('Informe diagnóstico — Factores de Riesgo Psicosocial en el Trabajo', level=0)
    p = doc.add_paragraph()
    p.add_run('NOM-035-STPS-2018').bold = True
    p2 = doc.add_paragraph()
    p2.add_run('Centro de trabajo: ').bold = True
    p2.add_run(str(ctx['tenant'].nombre))
    p3 = doc.add_paragraph()
    p3.add_run('Ciclo de evaluación: ').bold = True
    p3.add_run(str(ctx['ciclo']))
    p4 = doc.add_paragraph()
    p4.add_run('Fecha de generación del borrador: ').bold = True
    p4.add_run(ctx['fecha_generado'])
    doc.add_page_break()


def _add_datos_centro_trabajo(doc, ctx):
    datos = ctx['datos_centro_trabajo']
    _heading(doc, '2. Datos del centro de trabajo', level=1)
    _heading(doc, '2.1. Centro de trabajo', level=3)
    doc.add_paragraph(datos['nombre'])
    _heading(doc, '2.2. Domicilio', level=3)
    doc.add_paragraph(datos['direccion'] or '—')
    _heading(doc, '2.3. Actividad principal', level=3)
    doc.add_paragraph(datos['giro'] or '—')


def _add_objetivo(doc, ctx):
    _heading(doc, '3. Objetivo', level=1)
    _heading(doc, '3.1. Objetivo general', level=3)
    doc.add_paragraph(ctx['objetivo_general'])
    _heading(doc, '3.2. Objetivos específicos', level=3)
    for obj in ctx['objetivos_especificos']:
        doc.add_paragraph(obj, style='List Number')


def _add_definiciones(doc, ctx):
    _heading(doc, '4. Definiciones', level=1)
    for termino, definicion in ctx['definiciones']:
        p = doc.add_paragraph(style='List Bullet')
        p.add_run(f'{termino}: ').bold = True
        p.add_run(definicion)


def _add_justificacion_muestra(doc, ctx):
    jm = ctx['justificacion_muestra']
    _heading(doc, '5. Justificación de la muestra', level=1)
    doc.add_paragraph(jm['intro'])
    doc.add_paragraph(
        f"La población del centro de trabajo es de {jm['poblacion']} trabajadores; se evaluó "
        f"una muestra de {jm['muestra']} participantes, de los cuales {jm['hombres']} fueron "
        f"hombres y {jm['mujeres']} mujeres."
    )


def _add_metodologia(doc, ctx):
    met = ctx['metodologia']
    _heading(doc, '6. Metodología', level=1)
    _heading(doc, '6.1. Objetivo de la evaluación', level=3)
    doc.add_paragraph(met['objetivo_evaluacion'])

    _heading(doc, '6.2. Instrumentos utilizados', level=3)
    _simple_table(doc, ['Instrumento', 'Descripción'], met['instrumentos'])

    _heading(doc, '6.3. Procedimiento de aplicación', level=3)
    doc.add_paragraph('Antes de la aplicación:', style='Intense Quote')
    for paso in met['procedimiento_antes']:
        doc.add_paragraph(paso, style='List Number')
    doc.add_paragraph('Durante la aplicación del cuestionario:', style='Intense Quote')
    for paso in met['procedimiento_durante']:
        doc.add_paragraph(paso, style='List Number')
    doc.add_paragraph('Después de la aplicación del cuestionario:', style='Intense Quote')
    for paso in met['procedimiento_despues']:
        doc.add_paragraph(paso, style='List Number')

    _heading(doc, '6.4. Procesamiento a digital', level=3)
    doc.add_paragraph(met['procesamiento_digital'])

    _heading(doc, '6.5. Evaluación y análisis de resultados', level=3)
    doc.add_paragraph(met['evaluacion_analisis'])

    if ctx['tasas_respuesta']:
        _heading(doc, 'Tasa de respuesta por instrumento', level=3)
        _simple_table(
            doc,
            ['Instrumento', 'Aplicados', 'Respondidos', 'Tasa'],
            [[t['guia'], t['total'], t['completadas'], f"{t['pct']}%"] for t in ctx['tasas_respuesta']],
        )


def _add_grafica(doc, png_bytesio, width_cm=9):
    """Embebe una gráfica (BytesIO de PNG) centrada, si existe. No-op si
    `png_bytesio` es None (borrador sin `informe_extendido` nunca las pasa)."""
    if not png_bytesio:
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(png_bytesio, width=Cm(width_cm))


def _add_informe_demografico(doc, ctx):
    _heading(doc, '7. Informe demográfico', level=1)
    doc.add_paragraph(
        f"La muestra evaluada está conformada por {ctx['muestra']['total']} trabajadores que "
        f"participaron en al menos uno de los instrumentos aplicados."
    )
    graficas_muestra = ctx.get('graficas', {}).get('muestra', {})

    _heading(doc, '7.1. Informe de datos generales', level=3)
    cols_generales = {'Sexo', 'Grupo de edad', 'Nivel de estudios'}
    for tabla in ctx['muestra_tablas']:
        if tabla['col'] in cols_generales:
            _heading(doc, tabla['titulo'], level=4)
            _simple_table(
                doc, [tabla['col'], 'Trabajadores', '%'],
                [[d['label'], d['count'], f"{d['pct']}%"] for d in tabla['datos']],
            )
            _add_grafica(doc, graficas_muestra.get(tabla['col']))

    _heading(doc, '7.1.1. Informe de datos laborales', level=3)
    for tabla in ctx['muestra_tablas']:
        if tabla['col'] not in cols_generales:
            _heading(doc, tabla['titulo'], level=4)
            _simple_table(
                doc, [tabla['col'], 'Trabajadores', '%'],
                [[d['label'], d['count'], f"{d['pct']}%"] for d in tabla['datos']],
            )
            _add_grafica(doc, graficas_muestra.get(tabla['col']))


def _add_ats(doc, ctx):
    guia_i = ctx['guia_i']
    _heading(doc, '8. Informe de acontecimientos traumáticos severos', level=1)
    doc.add_paragraph(ctx['guia_i_definicion'])
    doc.add_paragraph(ctx['guia_i_texto'])
    if guia_i['total'] == 0:
        doc.add_paragraph('No se aplicó la Guía de Referencia I en este ciclo.')
        return
    doc.add_paragraph(
        f"De los {guia_i['total']} trabajadores que respondieron la Guía I, "
        f"{guia_i['requieren_atencion']} cumplen el criterio de caso positivo."
    )
    if guia_i['casos']:
        _simple_table(
            doc,
            ['Trabajador', 'Área', 'Acontecimiento (D1)', 'Síntomas (D2–D4)'],
            [[c['trabajador_nombre'], c['trabajador_area'], c['acontecimiento'], c['sintomas']]
             for c in guia_i['casos']],
        )


def _add_informe_diagnostico(doc, ctx):
    _heading(doc, '9. Informe diagnóstico sobre los factores de riesgo psicosocial y del entorno organizacional', level=1)

    _heading(doc, '9.1. Calificación final', level=3)
    doc.add_paragraph(
        f"Nivel de riesgo global de la organización: {ctx['nivel_global_label']} "
        f"(puntaje promedio: {ctx['promedio_global']})."
    )
    doc.add_paragraph(ctx['nivel_global_texto'])
    _simple_table(
        doc,
        ['Nivel de riesgo', 'Trabajadores', '%'],
        [[d['label'], d['count'], f"{d['pct']}%"] for d in ctx['distribucion']],
    )
    _add_grafica(doc, ctx.get('graficas', {}).get('distribucion'), width_cm=11)

    graficas_categorias = ctx.get('graficas', {}).get('categorias', {})
    graficas_dominios = ctx.get('graficas', {}).get('dominios', {})

    _heading(doc, '9.2. Calificaciones por categoría', level=3)
    _simple_table(
        doc,
        ['Categoría', 'Nulo', 'Bajo', 'Medio', 'Alto', 'Muy alto', 'Intervención', '%'],
        [[c['nombre'], c['dist']['nulo'], c['dist']['bajo'], c['dist']['medio'],
          c['dist']['alto'], c['dist']['muy_alto'], c['requieren_atencion'], f"{c['pct_intervencion']}%"]
         for c in ctx['categorias_agregadas']],
    )
    for c in ctx['categorias_agregadas']:
        _add_grafica(doc, graficas_categorias.get(c['nombre']), width_cm=8)

    _heading(doc, '9.3. Calificaciones por dominio', level=3)
    _simple_table(
        doc,
        ['Dominio', 'Nulo', 'Bajo', 'Medio', 'Alto', 'Muy alto', 'Intervención', '%'],
        [[d['nombre'], d['dist']['nulo'], d['dist']['bajo'], d['dist']['medio'],
          d['dist']['alto'], d['dist']['muy_alto'], d['requieren_atencion'], f"{d['pct_intervencion']}%"]
         for d in ctx['dominios_oficiales_agregados']],
    )
    for d in ctx['dominios_oficiales_agregados']:
        _add_grafica(doc, graficas_dominios.get(d['nombre']), width_cm=8)
    for dom in ctx['dominios_prioritarios']:
        _heading(doc, f"{dom['clave']} — {dom['nombre']}", level=4)
        if dom.get('mide'):
            p = doc.add_paragraph()
            p.add_run('Qué mide: ').italic = True
            p.add_run(dom['mide'])
        if dom.get('interpretacion'):
            p = doc.add_paragraph()
            p.add_run(dom['interpretacion']).italic = True

    _heading(doc, '9.4. Dimensiones', level=3)
    _simple_table(
        doc,
        ['Clave', 'Dimensión', 'Dominio', 'Promedio', 'Nivel'],
        [[dim['clave'], dim['nombre'], dim['dominio_oficial'],
          f"{dim['puntaje_promedio']}/{dim['puntaje_max']}",
          NIVEL_LABEL_DOCX.get(dim['categoria_predominante'], dim['categoria_predominante'])]
         for dim in ctx['dimensiones']],
    )


def _add_conclusiones(doc, ctx):
    c = ctx['conclusiones']
    _heading(doc, '10. Conclusiones', level=1)
    doc.add_paragraph(
        f"Conforme a la información analizada la calificación final, de una muestra "
        f"representativa de {c['muestra']} trabajadores, de un total de {c['poblacion']} "
        f"trabajadores; el {c['pct_riesgo']}% ({c['riesgo_alto']} trabajadores) perciben que "
        f"las condiciones de trabajo se tienen que mejorar."
    )
    if c['categorias_destacadas']:
        doc.add_paragraph(
            'De acuerdo a la información analizada en la agrupación correspondiente a las '
            'categorías, el personal presenta la mayor ponderación en:'
        )
        for cat in c['categorias_destacadas']:
            doc.add_paragraph(f"{cat['nombre']} — {cat['pct_intervencion']}%", style='List Bullet')
    if c['dominios_destacados']:
        doc.add_paragraph(
            'Por otra parte, en la agrupación correspondiente a los dominios, el personal '
            'presenta la mayor ponderación en:'
        )
        for dom in c['dominios_destacados']:
            doc.add_paragraph(f"{dom['nombre']} — {dom['pct_intervencion']}%", style='List Bullet')


def _add_recomendaciones(doc, ctx):
    _heading(doc, '11. Recomendaciones', level=1)

    if ctx.get('acciones_generales'):
        _heading(doc, '11.1. Recomendaciones generales', level=3)
        _simple_table(
            doc, ['Acción', 'Descripción'],
            [[titulo, texto] for titulo, texto in ctx['acciones_generales']],
        )

    recs_extendidas = ctx.get('recomendaciones_extendidas')
    if recs_extendidas is not None:
        _heading(doc, '11.2. Recomendaciones específicas', level=3)
        if not recs_extendidas:
            doc.add_paragraph(
                'Ningún dominio alcanzó nivel de riesgo Alto o Muy alto a nivel agregado. '
                'Se recomienda mantener las condiciones organizacionales actuales y reaplicar '
                'la evaluación en el siguiente ciclo normativo.'
            )
            return
        for idx, rec in enumerate(recs_extendidas, 1):
            _heading(doc, f"{idx}. {rec['dominio']} ({rec['pct_intervencion']}%)", level=4)
            doc.add_paragraph(rec['intro'])
            for titulo, texto in rec['bullets']:
                p = doc.add_paragraph(style='List Bullet')
                p.add_run(f'{titulo}: ').bold = True
                p.add_run(texto)
        return

    _heading(doc, '11.1. Recomendaciones específicas', level=3)
    if not ctx['recomendaciones']:
        doc.add_paragraph(
            'Ningún dominio alcanzó nivel de riesgo Alto o Muy alto a nivel agregado. '
            'Se recomienda mantener las condiciones organizacionales actuales y reaplicar '
            'la evaluación en el siguiente ciclo normativo.'
        )
        return
    for rec in ctx['recomendaciones']:
        p = doc.add_paragraph(style='List Bullet')
        if rec.get('urgencia'):
            p.add_run(f"[{rec['urgencia']}] ").bold = True
        p.add_run(rec['texto'])
        if rec.get('dominio'):
            p.add_run(f"  ({rec['dominio']})").italic = True


def _add_datos_responsable(doc, ctx):
    _heading(doc, '12. Datos del responsable de la evaluación', level=1)
    # En el borrador estos datos siempre quedan en blanco: la identidad del
    # revisor solo se inyecta al momento de aprobar (ver _inyectar_validacion_revisor).
    doc.add_paragraph('Nombre: ______________________________')
    doc.add_paragraph('Número de cédula profesional: ______________________________')
    doc.add_paragraph('Fecha de aprobación: ______________________________')


def _add_anexos(doc, ctx):
    anexos = ctx['anexos']
    _heading(doc, '13. Anexos', level=1)

    _heading(doc, '13.1. ATS y Calificación final', level=3)
    _simple_table(
        doc,
        ['Folio', 'Guía I — ATS', 'Calificación final', 'Nivel'],
        [[f['clave'], f['ats'], f['calificacion_final'],
          NIVEL_LABEL_DOCX.get(f['nivel_final'], f['nivel_final'])]
         for f in anexos['ats_final']],
    )

    _heading(doc, '13.2. Categorías', level=3)
    _simple_table(
        doc,
        ['Folio'] + anexos['categorias_columnas'],
        [[f['clave']] + [NIVEL_LABEL_DOCX.get(n, '—') if n else '—' for n in f['niveles']]
         for f in anexos['categorias_filas']],
    )

    _heading(doc, '13.3. Dominios', level=3)
    _simple_table(
        doc,
        ['Folio'] + anexos['dominios_columnas'],
        [[f['clave']] + [NIVEL_LABEL_DOCX.get(n, '—') if n else '—' for n in f['niveles']]
         for f in anexos['dominios_filas']],
    )

    _heading(doc, '13.4. Tabla de agrupación de dominios', level=3)
    _simple_table(
        doc,
        ['Categoría', 'Dominio', 'Dimensiones (D1-D14)'],
        [[f['categoria'], f['dominio'], ', '.join(f['claves'])] for f in anexos['agrupacion']],
    )


def build_reporte_psicologico_docx(ctx: dict) -> io.BytesIO:
    """Construye el borrador DOCX a partir del ctx de _build_psico_context(),
    siguiendo la misma estructura de 13 secciones que el PDF final aprobado."""
    doc = Document()
    _set_base_styles(doc)

    _add_portada(doc, ctx)
    _add_datos_centro_trabajo(doc, ctx)
    _add_objetivo(doc, ctx)
    _add_definiciones(doc, ctx)
    _add_justificacion_muestra(doc, ctx)
    _add_metodologia(doc, ctx)
    _add_informe_demografico(doc, ctx)
    _add_ats(doc, ctx)
    _add_informe_diagnostico(doc, ctx)
    _add_conclusiones(doc, ctx)
    _add_recomendaciones(doc, ctx)
    _add_datos_responsable(doc, ctx)
    _add_anexos(doc, ctx)

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf


def _add_portada_informe(doc, ctx):
    """Portada del Informe Diagnóstico completo (logo + título + tenant),
    sin la leyenda de borrador — es una descarga directa, no un documento
    pendiente de revisión."""
    logo_path = finders.find('documents/img/lear_logo.png')
    if logo_path:
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.add_run().add_picture(logo_path, width=Cm(6))

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(24)
    run = p_title.add_run('INFORME DIAGNÓSTICO')
    run.bold = True
    run.font.size = Pt(28)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p_sub.add_run('FACTORES DE RIESGO PSICOSOCIAL EN EL TRABAJO')
    run.bold = True
    run.font.size = Pt(13)

    p_nom = doc.add_paragraph()
    p_nom.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p_nom.add_run('NOM-035-STPS-2018')
    run.bold = True
    run.font.size = Pt(14)
    run.font.color.rgb = RGBColor(0xC8, 0x10, 0x2E)

    p_tenant = doc.add_paragraph()
    p_tenant.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tenant.paragraph_format.space_before = Pt(16)
    run = p_tenant.add_run(str(ctx['tenant'].nombre))
    run.bold = True
    run.font.size = Pt(12)

    p_fecha = doc.add_paragraph()
    p_fecha.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_fecha.add_run(f"Generado el {ctx['fecha_generado']}")

    doc.add_page_break()


def _add_indice(doc):
    """Índice con campo TOC de Word (se actualiza automáticamente al abrir,
    ver `_add_toc_update_fields`)."""
    _heading(doc, '1. Índice', level=1)
    para = doc.add_paragraph()
    for ftype, text in [('begin', None), (None, ' TOC \\o "1-3" \\h \\z \\u '),
                        ('separate', None), ('end', None)]:
        run = para.add_run()
        if ftype:
            fc = OxmlElement('w:fldChar')
            fc.set(qn('w:fldCharType'), ftype)
            run._r.append(fc)
        else:
            instr = OxmlElement('w:instrText')
            instr.set(qn('xml:space'), 'preserve')
            instr.text = text
            run._r.append(instr)
    doc.add_page_break()


def _add_toc_update_fields(doc):
    """Marca el documento para que Word actualice los campos (el índice) al
    abrirlo, sin que el usuario tenga que presionar F9 manualmente."""
    settings = doc.settings.element
    upd = OxmlElement('w:updateFields')
    upd.set(qn('w:val'), 'true')
    settings.append(upd)


def build_informe_diagnostico_docx(ctx: dict) -> io.BytesIO:
    """Construye el Informe Diagnóstico completo (portada + índice + 13
    secciones + gráficas), descarga directa sin flujo de aprobación.
    Requiere `ctx` generado con `informe_extendido=True` para incluir
    gráficas y recomendaciones extensas; si no, las secciones simplemente
    omiten las imágenes (`_add_grafica` es un no-op sin datos)."""
    doc = Document()
    _set_base_styles(doc)

    _add_portada_informe(doc, ctx)
    _add_indice(doc)
    _add_datos_centro_trabajo(doc, ctx)
    _add_objetivo(doc, ctx)
    _add_definiciones(doc, ctx)
    _add_justificacion_muestra(doc, ctx)
    _add_metodologia(doc, ctx)
    _add_informe_demografico(doc, ctx)
    _add_ats(doc, ctx)
    _add_informe_diagnostico(doc, ctx)
    _add_conclusiones(doc, ctx)
    _add_recomendaciones(doc, ctx)
    _add_datos_responsable(doc, ctx)
    _add_anexos(doc, ctx)

    _add_toc_update_fields(doc)

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf
