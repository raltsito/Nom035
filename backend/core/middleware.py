from core.managers import set_current_tenant


class TenantMiddleware:
    """
    Inyecta el tenant activo del usuario autenticado en el hilo actual.
    Debe ejecutarse despues de AuthenticationMiddleware.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)

        if user is not None and user.is_authenticated:
            tenant = getattr(user, 'tenant', None)
            set_current_tenant(tenant)
        else:
            set_current_tenant(None)

        response = self.get_response(request)

        set_current_tenant(None)
        return response
