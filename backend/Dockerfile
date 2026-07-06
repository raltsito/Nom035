FROM python:3.12-slim

# WeasyPrint, Pillow y psycopg necesitan estas libs de sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    libfontconfig1 \
    shared-mime-info \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

EXPOSE 8000

# migrate en el arranque: el releaseCommand de railway.toml no se ejecuta
# (Railway no lee ese archivo con la config actual del servicio) y desplegar
# codigo nuevo sin sus migraciones tumba el API (visto 2026-07-06).
CMD python manage.py migrate --noinput && \
    python manage.py collectstatic --noinput && \
    gunicorn intra_nom035.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
