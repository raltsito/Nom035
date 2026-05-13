"""
Importador de Excel para padrón de trabajadores (NOM-035 / Guía V).

Soporta los distintos formatos que usan las plantas de Lear:
- Nombres en una o tres columnas
- Columnas con títulos distintos para el mismo campo
- Valores de sexo como H/M, M/F, Hombre/Mujer
- Edades como entero, decimal o string "X años Y meses Z días"
- Jornadas como texto o código numérico (1/3/4)
- Tipo de personal como texto o código numérico
- Archivos con filas de título antes del encabezado real
"""

import re
import unicodedata
import uuid
from io import BytesIO

import openpyxl

from .models import Trabajador


# ---------------------------------------------------------------------------
# Normalización de texto base
# ---------------------------------------------------------------------------

def _norm(value):
    """Lowercase + sin acentos + sin caracteres especiales + strip."""
    if value is None:
        return ''
    text = str(value).strip().lower()
    text = unicodedata.normalize('NFKD', text)
    text = ''.join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def _clean(value):
    """Strip y title-case para almacenar en base de datos."""
    if value is None:
        return ''
    return str(value).strip()


# ---------------------------------------------------------------------------
# Mapeo de nombres de columnas → campo canónico
# ---------------------------------------------------------------------------

COLUMN_ALIASES = {
    'num_empleado': [
        'codigoemp', 'codigo', 'no. empleado', 'no empleado', 'num empleado',
        'numero de empleado', 'numero empleado', '#', 'no. empleado',
        'cod emp', 'employee id', 'id empleado',
    ],
    'nombre_completo': [
        'nombre del empleado',
    ],
    'nombre': [
        'nombre', 'nombres', 'nombre(s)',
    ],
    'apellido_paterno': [
        'apellido paterno', 'apellido', 'ap. paterno', 'ap paterno',
        'apellido1', 'primer apellido',
    ],
    'apellido_materno': [
        'apellido materno', 'apellido2', 'ap. materno', 'ap materno',
        'segundo apellido',
    ],
    'sexo': ['sexo', 'genero', 'genero/sexo'],
    'edad': ['edad'],
    'fecha_nacimiento': ['fecha nacimiento', 'fecha nac', 'fecha de nacimiento'],
    'estado_civil': ['estado civil', 'estado civil.', 'estado_civil'],
    'nivel_estudios': [
        'nivel de estudios', 'nivel estudios', 'escolaridad',
        'nivel de escolaridad',
    ],
    'puesto': [
        'puesto', 'ocupacion / profesion / puesto', 'ocupacion/profesion/puesto',
        'ocupacion / profesion /puesto', 'ocupacion/profesion/puesto',
        'puesto / cargo', 'cargo', 'ocupacion', 'profesion',
        'tipo de puesto', 'tipo puesto',
    ],
    'area': [
        'departamento', 'departamento/ seccion/ area',
        'departamento/seccion/area', 'departamento/ seccion/area',
        'area', 'seccion', 'area / departamento', 'departamento/area',
        'area/departamento', 'direccion departamento',
    ],
    'tipo_contratacion': [
        'tipo de contratacion', 'tipo contratacion',
        'tipo de contratacion', 'tipo contratacion',
    ],
    'tipo_personal': [
        'tipo de personal', 'tipo personal',
        'tipo de personal', 'tipo personal',
    ],
    'tipo_jornada': [
        'tipo jornada de trabajo', 'tipo de jornada de trabajo',
        'tipo de jornada', 'tipo jornada', 'turno',
        'tipo de jornada de trabajo', 'jornada',
    ],
    'rotacion_turnos': [
        'realiza rotacion de turnos', 'realiza rotacion de turno',
        'rotacion de turnos', 'rotacion de turno',
        'rotacion turnos', 'rotacion de turnos',
    ],
    'experiencia_anios': [
        'experiencia en anos', 'experiencia en a;os',
        'experiencia', 'experinecia en a;os',
        'experiencia laboral', 'anos de experiencia',
        'experiencia en anos', 'antiguedad',
    ],
    'tiempo_puesto_actual': [
        'tiempo en el puesto actual', 'tiempo en puesto actual',
        'tiempo de puesto actual', 'tiempo en puesto',
        'tiempo puesto actual', 'tiempo en el puesto',
    ],
}

# índice invertido: alias_normalizado → campo
_ALIAS_INDEX = {}
for _campo, _aliases in COLUMN_ALIASES.items():
    for _alias in _aliases:
        _ALIAS_INDEX[_norm(_alias)] = _campo


def _map_column(header):
    """Devuelve el campo canónico para un encabezado, o None si no reconoce."""
    return _ALIAS_INDEX.get(_norm(header))


# ---------------------------------------------------------------------------
# Normalización de valores por campo
# ---------------------------------------------------------------------------

def _norm_sexo(value, has_f_values=True):
    """
    has_f_values=True  → sistema M/F  (M=Masculino, F=Femenino)
    has_f_values=False → sistema H/M  (H=Hombre, M=Mujer)
    """
    v = _norm(value)
    if v in ('masculino', 'hombre', 'm', 'male') and has_f_values:
        return 'M'
    if v in ('femenino', 'mujer', 'f', 'female'):
        return 'F'
    # sistema H/M (sin F en los datos)
    if not has_f_values:
        if v == 'h':
            return 'M'
        if v == 'm':
            return 'F'
    # fallback con F en datos
    if v == 'm':
        return 'M'
    if v == 'f':
        return 'F'
    return ''


def _norm_estado_civil(value):
    v = _norm(value)
    if not v or v == 'none':
        return ''
    if 'soltero' in v or 'soltera' in v:
        return 'soltero'
    if 'casado' in v or 'casada' in v:
        return 'casado'
    if 'union' in v or 'libre' in v or 'concubinato' in v:
        return 'union_libre'
    if 'divorciado' in v or 'divorciada' in v or 'separado' in v:
        return 'divorciado'
    if 'viudo' in v or 'viuda' in v:
        return 'viudo'
    # Hermosillo usa códigos numéricos: 1=Soltero, 2=Casado
    try:
        code = int(float(value))
        return {1: 'soltero', 2: 'casado', 3: 'divorciado', 4: 'viudo', 5: 'union_libre'}.get(code, 'otro')
    except (ValueError, TypeError):
        pass
    return 'otro'


def _norm_nivel_estudios(value):
    v = _norm(value)
    if not v or v == 'none':
        return ''
    if 'primaria' in v:
        return 'primaria'
    if 'secundaria' in v:
        return 'secundaria'
    if 'bachillerato' in v or 'preparatoria' in v or 'prepa' in v or 'media superior' in v:
        return 'bachillerato'
    if 'tecnico' in v or 'tecnica' in v or 'carrera tecnica' in v:
        return 'tecnico'
    if 'ingenieria' in v or 'ingeniería' in v:
        return 'ingenieria'
    if 'licenciatura' in v:
        return 'licenciatura'
    if 'maestria' in v or 'doctorado' in v or 'posgrado' in v or 'postgrado' in v:
        return 'posgrado'
    return 'otro'


def _norm_tipo_personal(value):
    v = _norm(value)
    if not v or v == 'none':
        return ''
    if 'sindicalizado' in v or 'directo' in v:
        return 'sindicalizado'
    if 'indirecto' in v or 'confianza' in v:
        return 'confianza'
    if 'salary' in v or 'administrativo' in v or 'hourly admin' in v:
        return 'salary'
    # Códigos numéricos (Planta 726): 1=Directo, 2=Indirecto, 5=Salary
    try:
        code = int(float(value))
        return {1: 'sindicalizado', 2: 'confianza', 3: 'sindicalizado',
                5: 'salary', 8: 'confianza'}.get(code, 'otro')
    except (ValueError, TypeError):
        pass
    return 'otro'


def _norm_tipo_jornada(value):
    v = _norm(value)
    if not v or v == 'none':
        return ''
    if 'diurno' in v or 'diurna' in v:
        return 'diurno'
    if 'mixto' in v or 'mixta' in v:
        return 'mixto'
    if 'nocturno' in v or 'nocturna' in v:
        return 'nocturno'
    # Códigos numéricos (Pue-Pzc): 1=Diurno, 3=Mixto, 4=Nocturno
    try:
        code = int(float(value))
        return {1: 'diurno', 2: 'mixto', 3: 'mixto', 4: 'nocturno'}.get(code, '')
    except (ValueError, TypeError):
        pass
    # "Diurna - Nocturna - Mixta" → mixto
    if 'diurna' in v and 'nocturna' in v:
        return 'mixto'
    return ''


def _norm_rotacion(value):
    v = _norm(value)
    if not v or v == 'none':
        return None
    if v in ('si', 'sí', 'yes', 's', '1', 'true'):
        return True
    if v in ('no', 'n', '0', 'false'):
        return False
    return None


def _norm_edad(value):
    if value is None:
        return None
    # Ya es número
    try:
        return int(float(value))
    except (ValueError, TypeError):
        pass
    # String "24 años 7 meses 22 días" o "24a?os5 meses 6 dias"
    v = str(value)
    match = re.search(r'(\d+)\s*a', v, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


def _norm_experiencia(value):
    if value is None:
        return None
    # String "20 AÑOS 0 MESES 15 DIAS" o "0 años0 meses 24 dias"
    v = str(value).strip()
    try:
        return round(float(v), 1)
    except (ValueError, TypeError):
        pass
    match = re.search(r'(\d+)\s*a', v, re.IGNORECASE)
    meses = re.search(r'(\d+)\s*m', v, re.IGNORECASE)
    if match:
        years = int(match.group(1))
        months = int(meses.group(1)) if meses else 0
        return round(years + months / 12, 1)
    return None


def _norm_contratacion(value):
    v = _norm(value)
    if 'indeterminado' in v or 'individual' in v or 'indefinido' in v:
        return 'planta'
    if 'temporal' in v or 'determinado' in v or 'eventual' in v:
        return 'eventual'
    if 'subcontrat' in v or 'outsourc' in v:
        return 'subcontratado'
    return 'planta'


# ---------------------------------------------------------------------------
# Detección de fila de encabezados
# ---------------------------------------------------------------------------

def _detect_header_row(ws, max_scan=6):
    """
    Escanea las primeras `max_scan` filas y devuelve el índice (1-based)
    de la fila que parece ser el encabezado real.
    Criterio: la fila con más celdas cuyo valor normalizado coincide con
    algún alias conocido.
    """
    best_row = 1
    best_score = -1
    for row_idx in range(1, max_scan + 1):
        row = list(ws.iter_rows(min_row=row_idx, max_row=row_idx, values_only=True))[0]
        score = sum(1 for cell in row if cell and _map_column(str(cell)) is not None)
        if score > best_score:
            best_score = score
            best_row = row_idx
    return best_row


# ---------------------------------------------------------------------------
# Detección del sistema de codificación de sexo (H/M vs M/F)
# ---------------------------------------------------------------------------

def _detect_sex_system(rows, sex_col_idx):
    """Devuelve True si el archivo usa M=Masculino/F=Femenino, False si H=Hombre/M=Mujer."""
    values = set()
    for row in rows[:200]:
        v = _norm(row[sex_col_idx]) if sex_col_idx < len(row) else ''
        if v:
            values.add(v)
    # Si hay 'f' en los datos → sistema M/F
    return 'f' in values


# ---------------------------------------------------------------------------
# Parseo de nombre completo en una sola columna
# ---------------------------------------------------------------------------

def _split_nombre_completo(full_name):
    """
    Intenta dividir "APELLIDO_PAT APELLIDO_MAT NOMBRE(S)" en tres partes.
    Retorna (nombre, apellido_paterno, apellido_materno).
    """
    parts = _clean(full_name).split()
    if not parts:
        return '', '', ''
    if len(parts) == 1:
        return parts[0].title(), '', ''
    if len(parts) == 2:
        return parts[1].title(), parts[0].title(), ''
    # 3 o más palabras: ap_pat ap_mat nombre(s)
    ap_pat = parts[0].title()
    ap_mat = parts[1].title()
    nombre = ' '.join(p.title() for p in parts[2:])
    return nombre, ap_pat, ap_mat


# ---------------------------------------------------------------------------
# Función principal de importación
# ---------------------------------------------------------------------------

def importar_excel(file_obj, tenant):
    """
    Parsea un archivo Excel y crea/actualiza trabajadores del tenant.

    Retorna:
        {
            'importados': int,
            'actualizados': int,
            'omitidos': int,
            'errores': [{'fila': N, 'motivo': str}, ...],
        }
    """
    content = file_obj.read() if hasattr(file_obj, 'read') else file_obj
    wb = openpyxl.load_workbook(BytesIO(content), read_only=True, data_only=True)
    ws = wb.active

    header_row_idx = _detect_header_row(ws)

    # Leer encabezados
    headers_raw = list(ws.iter_rows(
        min_row=header_row_idx, max_row=header_row_idx, values_only=True
    ))[0]
    headers = [str(h).strip() if h is not None else '' for h in headers_raw]

    # Mapear índice de columna → campo canónico
    col_map = {}
    for idx, h in enumerate(headers):
        campo = _map_column(h)
        if campo and campo not in col_map:
            col_map[campo] = idx

    # Leer todas las filas de datos
    data_rows = list(ws.iter_rows(
        min_row=header_row_idx + 1, values_only=True
    ))
    wb.close()

    # Detectar sistema de sexo
    has_f = False
    if 'sexo' in col_map:
        has_f = _detect_sex_system(data_rows, col_map['sexo'])

    importados = actualizados = omitidos = 0
    errores = []

    for row_num, row in enumerate(data_rows, start=header_row_idx + 1):
        # Saltar filas completamente vacías
        if all(v is None or str(v).strip() == '' for v in row):
            continue

        def get(campo):
            idx = col_map.get(campo)
            if idx is None or idx >= len(row):
                return None
            v = row[idx]
            return v if v != '' else None

        try:
            # ── Nombre ──────────────────────────────────────────────────────
            if 'nombre_completo' in col_map:
                nombre, ap_pat, ap_mat = _split_nombre_completo(get('nombre_completo') or '')
            elif 'apellido_paterno' in col_map:
                nombre  = _clean(get('nombre') or '').title()
                ap_pat  = _clean(get('apellido_paterno') or '').title()
                ap_mat  = _clean(get('apellido_materno') or '').title()
            elif 'nombre' in col_map:
                raw = get('nombre')
                # En Hermosillo "Nombre" es un código numérico
                try:
                    int(float(raw))
                    nombre, ap_pat, ap_mat = '', '', ''
                except (ValueError, TypeError):
                    nombre, ap_pat, ap_mat = _split_nombre_completo(raw or '')
            else:
                nombre, ap_pat, ap_mat = '', '', ''

            if not nombre and not ap_pat:
                omitidos += 1
                continue

            # ── No. empleado ─────────────────────────────────────────────────
            raw_codigo = get('num_empleado')
            # Si "Nombre" en Hermosillo es int, úsalo como código
            if raw_codigo is None and 'nombre' in col_map:
                raw_n = get('nombre')
                try:
                    int(float(raw_n))
                    raw_codigo = raw_n
                except (ValueError, TypeError):
                    pass
            num_empleado = str(int(float(raw_codigo))) if raw_codigo is not None else ''

            # ── Campos Guía V ────────────────────────────────────────────────
            sexo            = _norm_sexo(get('sexo'), has_f)
            edad            = _norm_edad(get('edad') or get('fecha_nacimiento'))
            estado_civil    = _norm_estado_civil(get('estado_civil'))
            nivel_estudios  = _norm_nivel_estudios(get('nivel_estudios'))
            tipo_personal   = _norm_tipo_personal(get('tipo_personal'))
            tipo_jornada    = _norm_tipo_jornada(get('tipo_jornada'))
            rotacion_turnos = _norm_rotacion(get('rotacion_turnos'))
            experiencia     = _norm_experiencia(get('experiencia_anios'))
            tiempo_puesto   = _norm_experiencia(get('tiempo_puesto_actual'))
            tipo_contrat    = _norm_contratacion(get('tipo_contratacion') or '')
            puesto          = _clean(get('puesto') or '').title()
            area            = _clean(get('area') or '').title()

            defaults = dict(
                nombre=nombre or ap_pat,
                apellido_paterno=ap_pat,
                apellido_materno=ap_mat,
                puesto=puesto,
                area=area,
                tipo_contratacion=tipo_contrat,
                sexo=sexo,
                edad=edad,
                estado_civil=estado_civil,
                nivel_estudios=nivel_estudios,
                tipo_personal=tipo_personal,
                tipo_jornada=tipo_jornada,
                rotacion_turnos=rotacion_turnos,
                experiencia_anios=experiencia,
                tiempo_puesto_actual=tiempo_puesto,
            )

            if num_empleado:
                obj, created = Trabajador.objects.update_or_create(
                    tenant=tenant,
                    num_empleado=num_empleado,
                    defaults=defaults,
                )
            else:
                # Sin código de empleado: buscar por nombre completo
                # Si hay duplicados de nombre, actualizar el primero
                qs = Trabajador.objects.filter(
                    tenant=tenant,
                    nombre=defaults['nombre'],
                    apellido_paterno=defaults['apellido_paterno'],
                )
                if qs.exists():
                    obj = qs.first()
                    for k, v in defaults.items():
                        setattr(obj, k, v)
                    obj.save()
                    created = False
                else:
                    obj = Trabajador.objects.create(tenant=tenant, **defaults)
                    created = True

            if created:
                importados += 1
            else:
                actualizados += 1

        except Exception as exc:
            errores.append({'fila': row_num, 'motivo': str(exc)})

    return {
        'importados': importados,
        'actualizados': actualizados,
        'omitidos': omitidos,
        'errores': errores,
    }
