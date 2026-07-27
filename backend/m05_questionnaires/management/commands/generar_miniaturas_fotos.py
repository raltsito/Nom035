"""Genera las miniaturas de las fotos ya capturadas (backfill).

Las fotos anteriores a la galería del informe fotográfico se guardaron solo
en 640 px; este comando crea su miniatura de 220 px para que el listado no
tenga que recomprimir nada en caliente.

    python manage.py generar_miniaturas_fotos [--tenant NOMBRE] [--rehacer]
"""
from django.core.management.base import BaseCommand
from django.db.models import Q

from m05_questionnaires.models import AplicacionFoto
from m05_questionnaires.views import generar_miniatura


class Command(BaseCommand):
    help = 'Genera la miniatura de las fotos capturadas que aún no la tienen.'

    def add_arguments(self, parser):
        parser.add_argument('--tenant', help='Limitar a una planta por nombre.')
        parser.add_argument('--rehacer', action='store_true',
                            help='Regenerar también las miniaturas existentes.')
        parser.add_argument('--lote', type=int, default=200,
                            help='Fotos por lote (default 200).')

    def handle(self, *args, **opciones):
        qs = AplicacionFoto.objects.filter(estado='capturada').exclude(foto=None)
        if opciones.get('tenant'):
            qs = qs.filter(tenant__nombre__iexact=opciones['tenant'])
        if not opciones.get('rehacer'):
            qs = qs.filter(Q(miniatura=None) | Q(miniatura_tamanio=0))

        total = qs.count()
        if not total:
            self.stdout.write('No hay fotos pendientes de miniatura.')
            return

        self.stdout.write(f'Generando miniaturas para {total} fotos...')
        lote = max(1, opciones['lote'])
        hechas = fallidas = bytes_generados = 0
        ids = list(qs.values_list('id', flat=True))

        for inicio in range(0, len(ids), lote):
            pendientes = []
            for foto in AplicacionFoto.objects.filter(id__in=ids[inicio:inicio + lote]):
                mini = generar_miniatura(bytes(foto.foto))
                if mini is None:
                    fallidas += 1
                    continue
                foto.miniatura = mini
                foto.miniatura_tamanio = len(mini)
                pendientes.append(foto)
                bytes_generados += len(mini)
            if pendientes:
                AplicacionFoto.objects.bulk_update(
                    pendientes, ['miniatura', 'miniatura_tamanio'])
                hechas += len(pendientes)
            self.stdout.write(f'  {hechas}/{total}')

        self.stdout.write(self.style.SUCCESS(
            f'Listo: {hechas} miniaturas ({bytes_generados / 1024 / 1024:.1f} MB en total)'
            + (f', {fallidas} ilegibles omitidas.' if fallidas else '.')
        ))
