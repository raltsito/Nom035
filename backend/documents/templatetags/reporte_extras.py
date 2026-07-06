from django import template

register = template.Library()

_NIVEL_LABELS = {
    'nulo':     'Nulo',
    'bajo':     'Bajo',
    'medio':    'Medio',
    'alto':     'Alto',
    'muy_alto': 'Muy alto',
}


@register.filter
def nivel_label(clave):
    """'muy_alto' -> 'Muy alto'. Evita el bug de `cut:"_"|capfirst` (da 'Muyalto')."""
    return _NIVEL_LABELS.get(clave, clave)
