"""Post-procesamiento del Informe Diagnóstico DOCX: actualización REAL del
índice (TOC) y de los campos de página con LibreOffice headless.

`w:updateFields` en settings.xml solo le PIDE a Word que actualice campos al
abrir; si el usuario no lo permite (o abre el archivo en otro visor) el índice
queda vacío, con todas las páginas en «1» o con «¡Error! Marcador no
definido.». Aquí el DOCX descargado ya viaja con el índice poblado:

1. Se inicializa un perfil temporal de LibreOffice (primer arranque con una
   conversión trivial). Sembrar la macro ANTES del primer arranque no sirve:
   LibreOffice regenera la configuración Basic al crear el perfil.
2. Se siembra en ese perfil una macro Basic
   (`Standard.Module1.ActualizarCampos`) que carga el documento con
   UpdateDocMode.FULL_UPDATE, refresca la paginación, actualiza todos los
   DocumentIndexes DOS veces (la primera pasada puede mover la paginación) y
   lo guarda con el filtro «MS Word 2007 XML».
3. Se invoca `soffice --headless` sobre ese perfil. Cada invocación usa un
   perfil y directorio temporal propios: es determinista y seguro frente a
   invocaciones concurrentes.

La macro vive en el perfil (no en el documento), por lo que la seguridad de
macros de LibreOffice no la bloquea.

Requisito del documento: el campo TOC debe llevar un RESULTADO provisional
(texto entre los fldChar separate/end). Sin él, el importador de LibreOffice
ignora el campo y `DocumentIndexes` queda vacío (docx_builder._add_field ya
lo garantiza).
"""
import logging
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)


class ErrorPostprocesoDocx(RuntimeError):
    """No fue posible actualizar el índice del DOCX con LibreOffice."""


_MACRO_XBA = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE script:module PUBLIC "-//OpenOffice.org//DTD OfficeDocument 1.0//EN" "module.dtd">
<script:module xmlns:script="http://openoffice.org/2000/script" script:name="Module1" script:language="StarBasic">Sub ActualizarCampos()
  Dim sIn As String, sOut As String
  sIn = Environ("NOM035_DOCX_IN")
  sOut = Environ("NOM035_DOCX_OUT")
  Dim oArgs(1) As New com.sun.star.beans.PropertyValue
  oArgs(0).Name = "Hidden" : oArgs(0).Value = True
  oArgs(1).Name = "UpdateDocMode" : oArgs(1).Value = com.sun.star.document.UpdateDocMode.FULL_UPDATE
  Dim oDoc
  oDoc = StarDesktop.loadComponentFromURL(ConvertToURL(sIn), "_blank", 0, oArgs())
  Dim iPasada%, i%
  For iPasada = 1 To 2
    oDoc.refresh()
    If Not IsNull(oDoc.TextFields) Then oDoc.TextFields.refresh()
    For i = 0 To oDoc.DocumentIndexes.Count - 1
      oDoc.DocumentIndexes.getByIndex(i).update()
    Next i
  Next iPasada
  Dim oSave(0) As New com.sun.star.beans.PropertyValue
  oSave(0).Name = "FilterName" : oSave(0).Value = "MS Word 2007 XML"
  oDoc.storeToURL(ConvertToURL(sOut), oSave())
  oDoc.close(False)
End Sub
</script:module>'''

_SCRIPT_XLB = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE library:library PUBLIC "-//OpenOffice.org//DTD OfficeDocument 1.0//EN" "library.dtd">
<library:library xmlns:library="http://openoffice.org/2000/library" library:name="Standard" library:readonly="false" library:passwordprotected="false">
 <library:element library:name="Module1"/>
</library:library>'''

_SCRIPT_XLC = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE library:libraries PUBLIC "-//OpenOffice.org//DTD OfficeDocument 1.0//EN" "libraries.dtd">
<library:libraries xmlns:library="http://openoffice.org/2000/library" xmlns:xlink="http://www.w3.org/1999/xlink">
 <library:library library:name="Standard" xlink:href="$(USER)/basic/Standard/script.xlb/" xlink:type="simple" library:link="false"/>
</library:libraries>'''


_SOFFICE_CACHE = {'resuelto': False, 'ruta': None}


def localizar_soffice():
    """Ruta del ejecutable de LibreOffice, o None si no está disponible.

    La comprobación es por EJECUCIÓN (`soffice --version`), no por
    existencia del archivo: en instalaciones virtualizadas de Windows
    (Store/MSIX) la ruta se puede ejecutar aunque `Path.exists()` devuelva
    False. El resultado se cachea para el resto del proceso."""
    if _SOFFICE_CACHE['resuelto']:
        return _SOFFICE_CACHE['ruta']

    candidatos = [os.environ.get('LIBREOFFICE_BIN')]
    candidatos.append(shutil.which('soffice'))
    candidatos.extend([
        '/usr/bin/soffice',
        '/usr/bin/libreoffice',
        '/usr/local/bin/soffice',
        r'C:\Program Files\LibreOffice\program\soffice.exe',
        r'C:\Program Files (x86)\LibreOffice\program\soffice.exe',
    ])
    ruta = None
    for c in candidatos:
        if not c:
            continue
        if Path(c).exists():
            ruta = c
            break
        try:
            res = subprocess.run([c, '--version'], capture_output=True, timeout=60)
            if res.returncode == 0:
                ruta = c
                break
        except (OSError, subprocess.TimeoutExpired):
            continue
    _SOFFICE_CACHE.update(resuelto=True, ruta=ruta)
    return ruta


def _sembrar_perfil(perfil: Path):
    basic = perfil / 'user' / 'basic'
    (basic / 'Standard').mkdir(parents=True, exist_ok=True)
    (basic / 'script.xlc').write_text(_SCRIPT_XLC, encoding='utf-8')
    (basic / 'Standard' / 'script.xlb').write_text(_SCRIPT_XLB, encoding='utf-8')
    (basic / 'Standard' / 'Module1.xba').write_text(_MACRO_XBA, encoding='utf-8')


def actualizar_campos_docx(docx_bytes: bytes, timeout=180) -> bytes:
    """Devuelve el DOCX con el índice y los campos actualizados por
    LibreOffice. Lanza ErrorPostprocesoDocx si LibreOffice no está disponible
    o la actualización no produce un índice poblado."""
    soffice = localizar_soffice()
    if not soffice:
        raise ErrorPostprocesoDocx(
            'LibreOffice (soffice) no está disponible; define LIBREOFFICE_BIN '
            'o instala libreoffice-writer.'
        )

    with tempfile.TemporaryDirectory(prefix='nom035_toc_') as tmp:
        tmp = Path(tmp)
        entrada = tmp / 'informe_in.docx'
        salida = tmp / 'informe_out.docx'
        perfil = tmp / 'perfil_lo'
        entrada.write_bytes(docx_bytes)

        base_cmd = [
            soffice, '--headless', '--norestore', '--nologo', '--nolockcheck',
            f'-env:UserInstallation={perfil.as_uri()}',
        ]

        # Paso 1: primer arranque para que LO cree el perfil (una conversión
        # trivial); solo después puede sembrarse la biblioteca Basic.
        dummy = tmp / 'bootstrap.txt'
        dummy.write_text('nom035', encoding='utf-8')
        try:
            subprocess.run(
                base_cmd + ['--convert-to', 'pdf', '--outdir', str(tmp), str(dummy)],
                capture_output=True, timeout=timeout,
            )
        except subprocess.TimeoutExpired as exc:
            raise ErrorPostprocesoDocx(
                f'LibreOffice excedió {timeout}s al inicializar el perfil') from exc

        # Paso 2: sembrar la macro en el perfil ya inicializado.
        _sembrar_perfil(perfil)

        # Paso 3: ejecutar la macro de actualización.
        env = dict(os.environ)
        env['NOM035_DOCX_IN'] = str(entrada)
        env['NOM035_DOCX_OUT'] = str(salida)
        try:
            res = subprocess.run(
                base_cmd + ['macro:///Standard.Module1.ActualizarCampos'],
                env=env, capture_output=True, timeout=timeout,
            )
        except subprocess.TimeoutExpired as exc:
            raise ErrorPostprocesoDocx(f'LibreOffice excedió {timeout}s') from exc

        if not salida.exists():
            raise ErrorPostprocesoDocx(
                'LibreOffice no produjo el DOCX actualizado '
                f'(rc={res.returncode}, stderr={res.stderr[:500]!r})'
            )
        actualizado = salida.read_bytes()

    _verificar_toc_poblado(actualizado)
    return actualizado


def _verificar_toc_poblado(docx_bytes: bytes):
    """El DOCX entregado debe traer un índice con entradas reales y sin
    '¡Error! Marcador no definido.'. Los estilos de entrada pueden llamarse
    TDC1/TDC3 (Word en español) o TOC1/TOC3 (export de LibreOffice)."""
    import io
    import re
    import zipfile

    with zipfile.ZipFile(io.BytesIO(docx_bytes)) as z:
        xml = z.read('word/document.xml').decode('utf-8', errors='replace')
    if 'Marcador no definido' in xml or 'Bookmark not defined' in xml:
        raise ErrorPostprocesoDocx('El índice quedó con marcadores rotos.')
    if 'Índice pendiente de actualización' in xml:
        raise ErrorPostprocesoDocx('El índice conserva el texto provisional.')
    entradas_toc = len(re.findall(r'w:pStyle w:val="(?:TDC|TOC)\d', xml))
    if entradas_toc < 10:
        raise ErrorPostprocesoDocx(
            f'El índice no quedó poblado (solo {entradas_toc} entradas).'
        )
