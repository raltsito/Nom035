"""Settings para la suite de pruebas: BD SQLite autocontenida.

El proyecto no usa características exclusivas de PostgreSQL (JSONField es
portable), así que las pruebas no dependen de que el Postgres local o el
túnel a Railway estén levantados. Uso:

    python manage.py test --settings=intra_nom035.settings.testing
"""
from .development import *  # noqa: F401,F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'test_local.sqlite3',  # noqa: F405
    }
}

# Sin postproceso estricto por defecto: cada prueba lo activa si lo necesita.
INFORME_TOC_ESTRICTO = False
