"""Matriz de resultados individuales: una fila por trabajador con su nivel de
riesgo en cada dominio oficial, cada categoría oficial y el resultado final
(Tabla 6, Guía de Referencia III).

Es la fuente única de la tabla que se muestra en /resultados y del Excel
descargable, para que la vista previa (solo los más riesgosos) y el archivo
completo nunca puedan discrepar.
"""
from .models import ResultadoAplicacion
from .scoring import CATEGORIAS_OFICIALES, CRITERIOS_GUIA_I, DOMINIOS_OFICIALES

# Orden de severidad: mayor número = más riesgoso. `sin_calificar` queda al
# final porque no es un nivel de riesgo, sino un cuestionario sin clasificar.
SEVERIDAD = {
    'muy_alto': 5,
    'alto':     4,
    'medio':    3,
    'bajo':     2,
    'nulo':     1,
}

# Etiqueta corta de cada nivel para las celdas del Excel.
ETIQUETAS = {
    'muy_alto':      'Muy alto',
    'alto':          'Alto',
    'medio':         'Medio',
    'bajo':          'Bajo',
    'nulo':          'Nulo',
    'sin_calificar': 'Sin calificar',
    # Exclusivas de Guía I (no son niveles de riesgo, son un dictamen binario).
    'requiere_atencion': 'Requiere atención',
    'sin_indicadores':   'Sin indicadores',
}

# Claves de los dominios oficiales tal como las persiste el motor (D1…D10).
COLUMNAS_DOMINIOS = [
    {'clave': f'D{i}', 'nombre': nombre, 'orden': i}
    for i, nombre in enumerate(DOMINIOS_OFICIALES, 1)
]

COLUMNAS_CATEGORIAS = [
    {'orden': i, 'nombre': nombre}
    for i, nombre in enumerate(CATEGORIAS_OFICIALES, 1)
]


def _celda(registro):
    """Celda de la matriz a partir de un ResultadoDominioOficial/Categoria."""
    if registro is None:
        return {'categoria': None, 'puntaje': None, 'puntaje_max': None, 'porcentaje': None}
    pm = registro.puntaje_max or 0
    return {
        'categoria':   registro.categoria,
        'puntaje':     registro.puntaje,
        'puntaje_max': pm,
        # Un dominio sin ítems aplicables (filtros de la GR.III) queda en 0/0:
        # se reporta como no aplicable en lugar de forzar un porcentaje.
        'porcentaje':  round(registro.puntaje / pm * 100) if pm else None,
    }


def construir_matriz(tenant, ciclo_id, limite=None):
    """Devuelve (filas, total) de la matriz del ciclo, ordenadas de mayor a
    menor riesgo. Con `limite` se recortan las filas devueltas, pero `total`
    siempre refleja el universo completo de trabajadores evaluados."""
    qs = ResultadoAplicacion.objects.filter(
        aplicacion__tenant=tenant,
        aplicacion__ciclo_id=ciclo_id,
        aplicacion__cuestionario__clave='III',
    ).select_related(
        'aplicacion__trabajador',
    ).prefetch_related('dominios_oficiales', 'categorias')

    filas = []
    for resultado in qs:
        trabajador = resultado.aplicacion.trabajador
        por_clave  = {d.clave: d for d in resultado.dominios_oficiales.all()}
        por_orden  = {c.orden: c for c in resultado.categorias.all()}

        dominios   = [_celda(por_clave.get(col['clave'])) for col in COLUMNAS_DOMINIOS]
        categorias = [_celda(por_orden.get(col['orden'])) for col in COLUMNAS_CATEGORIAS]

        sev_final = SEVERIDAD.get(resultado.categoria, 0)
        # Desempate: entre dos trabajadores con el mismo nivel final, primero
        # el que acumula más dominios en alto/muy alto y mayor puntaje.
        dominios_criticos = sum(
            1 for d in dominios if SEVERIDAD.get(d['categoria'], 0) >= 4
        )
        pm = resultado.puntaje_max or 0

        filas.append({
            'resultado_id':       resultado.id,
            'num_empleado':       trabajador.num_empleado or '',
            'trabajador_nombre':  trabajador.nombre_completo,
            'trabajador_area':    trabajador.area or 'Sin área',
            'trabajador_puesto':  trabajador.puesto or '',
            'estatus_validacion': resultado.estatus_validacion,
            'dominios':           dominios,
            'categorias':         categorias,
            'final': {
                'categoria':   resultado.categoria,
                'puntaje':     resultado.puntaje_total,
                'puntaje_max': pm,
                'porcentaje':  round(resultado.puntaje_total / pm * 100) if pm else None,
            },
            'severidad':          sev_final,
            'dominios_criticos':  dominios_criticos,
        })

    filas.sort(
        key=lambda f: (
            f['severidad'],
            f['dominios_criticos'],
            f['final']['puntaje'],
        ),
        reverse=True,
    )

    total = len(filas)
    if limite is not None and limite > 0:
        filas = filas[:limite]
    return filas, total


# ---------------------------------------------------------------------------
# Guía I — Acontecimientos traumáticos severos
# ---------------------------------------------------------------------------
# La Guía I no produce niveles de riesgo: es un dictamen binario (¿el
# trabajador requiere valoración clínica?) a partir de cuántos "Sí" acumula
# cada sección frente a su criterio (GR.I inciso b). Las columnas son las 4
# secciones más el dictamen final.
COLUMNAS_SECCIONES_GUIA_I = [
    {'clave': 'D1', 'romano': 'I',   'nombre': 'Acontecimiento traumático severo',
     'criterio': CRITERIOS_GUIA_I['D1']},
    {'clave': 'D2', 'romano': 'II',  'nombre': 'Recuerdos persistentes',
     'criterio': CRITERIOS_GUIA_I['D2']},
    {'clave': 'D3', 'romano': 'III', 'nombre': 'Esfuerzo por evitar circunstancias parecidas',
     'criterio': CRITERIOS_GUIA_I['D3']},
    {'clave': 'D4', 'romano': 'IV',  'nombre': 'Afectación',
     'criterio': CRITERIOS_GUIA_I['D4']},
]

# Severidad para ordenar la vista previa: primero quien requiere atención
# clínica y después lo que quedó sin clasificar (necesita revisión humana).
SEVERIDAD_GUIA_I = {
    'requiere_atencion': 3,
    'sin_calificar':     2,
    'sin_indicadores':   1,
}


def _celda_seccion(registro, columna):
    """Celda de una sección de Guía I: cuántos "Sí" y si alcanza el criterio.

    El color NO es un nivel de riesgo de la NOM-035; codifica el estado del
    criterio: alcanzado (alto), respuestas afirmativas por debajo del criterio
    (bajo) o sin afirmativas (nulo). La Sección I es el filtro de entrada, por
    eso al alcanzarse se marca en medio y no en alto: haber vivido un
    acontecimiento no implica por sí solo requerir atención."""
    criterio = columna['criterio']
    if registro is None:
        return {'positivos': None, 'total': None, 'criterio': criterio,
                'cumple': None, 'categoria': None}

    positivos = registro.puntaje
    cumple    = positivos >= criterio
    if cumple:
        categoria = 'medio' if columna['clave'] == 'D1' else 'alto'
    elif positivos > 0:
        categoria = 'bajo'
    else:
        categoria = 'nulo'

    return {
        'positivos': positivos,
        'total':     registro.puntaje_max,
        'criterio':  criterio,
        'cumple':    cumple,
        'categoria': categoria,
    }


def construir_matriz_guia_i(tenant, ciclo_id, limite=None):
    """Devuelve (filas, total) de la matriz de Guía I del ciclo, ordenada de
    mayor a menor necesidad de atención. `limite` recorta las filas devueltas;
    `total` siempre refleja a todos los trabajadores evaluados."""
    qs = ResultadoAplicacion.objects.filter(
        aplicacion__tenant=tenant,
        aplicacion__ciclo_id=ciclo_id,
        aplicacion__cuestionario__clave='I',
    ).select_related(
        'aplicacion__trabajador',
    ).prefetch_related('dominios__dominio')

    filas = []
    for resultado in qs:
        trabajador = resultado.aplicacion.trabajador
        por_clave  = {rd.dominio.clave: rd for rd in resultado.dominios.all()}

        secciones = [
            _celda_seccion(por_clave.get(col['clave']), col)
            for col in COLUMNAS_SECCIONES_GUIA_I
        ]
        # Secciones II-IV que alcanzan su criterio: son las que disparan el
        # dictamen, la I sola no basta.
        criterios_cumplidos = sum(1 for c in secciones[1:] if c['cumple'])

        filas.append({
            'resultado_id':       resultado.id,
            'num_empleado':       trabajador.num_empleado or '',
            'trabajador_nombre':  trabajador.nombre_completo,
            'trabajador_area':    trabajador.area or 'Sin área',
            'trabajador_puesto':  trabajador.puesto or '',
            'estatus_validacion': resultado.estatus_validacion,
            'secciones':          secciones,
            'final': {
                'categoria':         resultado.categoria,
                'requiere_atencion': resultado.requiere_atencion,
            },
            'severidad':           SEVERIDAD_GUIA_I.get(resultado.categoria, 0),
            'criterios_cumplidos': criterios_cumplidos,
            'positivos_total':     resultado.puntaje_total,
        })

    filas.sort(
        key=lambda f: (f['severidad'], f['criterios_cumplidos'], f['positivos_total']),
        reverse=True,
    )

    total = len(filas)
    if limite is not None and limite > 0:
        filas = filas[:limite]
    return filas, total
