GUIA_ORDEN = ('V', 'III', 'I')


def obtener_clave_guia_pendiente(trabajador, ciclo):
    """Devuelve la siguiente clave de guia pendiente para un trabajador en un ciclo."""
    from .models import Aplicacion

    completadas = set(
        Aplicacion.objects.filter(
            tenant=trabajador.tenant,
            trabajador=trabajador,
            ciclo=ciclo,
            cuestionario__clave__in=GUIA_ORDEN,
            estado='completado',
        ).values_list('cuestionario__clave', flat=True)
    )
    return obtener_clave_guia_pendiente_desde_completadas(completadas)


def obtener_clave_guia_pendiente_desde_completadas(completadas):
    for clave in GUIA_ORDEN:
        if clave not in completadas:
            return clave
    return None


def obtener_guia_pendiente(trabajador, ciclo):
    """Devuelve el cuestionario pendiente o None si ya completo todas las guias."""
    from .models import Cuestionario

    clave = obtener_clave_guia_pendiente(trabajador, ciclo)
    if clave is None:
        return None
    return Cuestionario.objects.filter(clave=clave).first()


def obtener_claves_completadas_por_trabajador(ciclo, trabajadores=None, tenant=None):
    """Indice reusable para lotes: {trabajador_id: {'V', 'III'}}."""
    from .models import Aplicacion

    qs = Aplicacion.objects.filter(
        ciclo=ciclo,
        cuestionario__clave__in=GUIA_ORDEN,
        estado='completado',
    ).select_related('cuestionario')

    if tenant is not None:
        qs = qs.filter(tenant=tenant)
    if trabajadores is not None:
        qs = qs.filter(trabajador_id__in=[t.id for t in trabajadores])

    completadas = {}
    for aplicacion in qs:
        completadas.setdefault(aplicacion.trabajador_id, set()).add(aplicacion.cuestionario.clave)
    return completadas
