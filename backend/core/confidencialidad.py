"""Umbral de confidencialidad para resultados agregados NOM-035.

Los resultados de grupos con menos de `umbral_confidencialidad()` personas no
deben mostrarse (podrían identificar respuestas individuales). Configurable
por settings (`NOM035_UMBRAL_CONFIDENCIALIDAD`) o variable de entorno del
mismo nombre; por defecto 5. Clientes con políticas más estrictas pueden
subirlo a 10.
"""
import os

from django.conf import settings

ETIQUETA_RESERVADO = 'Dato reservado por confidencialidad'
_DEFAULT = 5


def umbral_confidencialidad() -> int:
    valor = getattr(
        settings, 'NOM035_UMBRAL_CONFIDENCIALIDAD',
        os.environ.get('NOM035_UMBRAL_CONFIDENCIALIDAD', _DEFAULT),
    )
    try:
        return max(0, int(valor))
    except (TypeError, ValueError):
        return _DEFAULT


def grupo_reservado(n: int) -> bool:
    """True si un grupo de tamaño `n` debe reservarse (n < umbral)."""
    return n < umbral_confidencialidad()
