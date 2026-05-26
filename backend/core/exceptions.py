import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


def standard_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        return Response(
            {
                'data': None,
                'meta': {},
                'errors': response.data,
            },
            status=response.status_code,
        )

    # Excepción no manejada por DRF — loguear el traceback completo
    view = context.get('view')
    logger.exception('Excepción no manejada en %s: %s', view, exc)

    return Response(
        {
            'data': None,
            'meta': {},
            'errors': {'detail': 'Error interno del servidor.'},
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
