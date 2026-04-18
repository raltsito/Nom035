from django.http import HttpResponse
from django.template.loader import render_to_string
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.permissions import IsTenantAdmin
from .models import PoliticaPrevension
from .serializers import PoliticaPrevencionSerializer

try:
    from weasyprint import HTML as WeasyHTML
    WEASYPRINT_OK = True
except Exception:
    WEASYPRINT_OK = False


def _wrap(data, meta=None, errors=None, code=status.HTTP_200_OK):
    return Response({'data': data, 'meta': meta or {}, 'errors': errors}, status=code)


class PoliticaViewSet(viewsets.ModelViewSet):
    permission_classes = (IsTenantAdmin,)
    serializer_class   = PoliticaPrevencionSerializer

    def get_queryset(self):
        qs       = PoliticaPrevension.objects.filter(
            tenant=self.request.user.tenant
        ).select_related('ciclo')
        ciclo_id = self.request.query_params.get('ciclo_id')
        if ciclo_id:
            qs = qs.filter(ciclo_id=ciclo_id)
        return qs

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        return _wrap(PoliticaPrevencionSerializer(qs, many=True).data, meta={'count': qs.count()})

    def retrieve(self, request, *args, **kwargs):
        return _wrap(PoliticaPrevencionSerializer(self.get_object()).data)

    def create(self, request, *args, **kwargs):
        serializer = PoliticaPrevencionSerializer(data=request.data)
        if serializer.is_valid():
            politica = serializer.save(tenant=request.user.tenant)
            return _wrap(PoliticaPrevencionSerializer(politica).data, code=status.HTTP_201_CREATED)
        return _wrap(None, errors=serializer.errors, code=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial  = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = PoliticaPrevencionSerializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            politica = serializer.save()
            return _wrap(PoliticaPrevencionSerializer(politica).data)
        return _wrap(None, errors=serializer.errors, code=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()
        return _wrap(None)

    @action(detail=True, methods=['post'], url_path='aprobar')
    def aprobar(self, request, pk=None):
        from datetime import date
        instance = self.get_object()
        instance.estado           = 'vigente'
        instance.fecha_aprobacion = instance.fecha_aprobacion or date.today()
        instance.save(update_fields=['estado', 'fecha_aprobacion'])
        return _wrap(PoliticaPrevencionSerializer(instance).data)

    @action(detail=True, methods=['get'], url_path='pdf')
    def pdf(self, request, pk=None):
        politica = self.get_object()
        ctx = {
            'tenant':   request.user.tenant,
            'politica': politica,
            'ciclo':    politica.ciclo,
        }
        html_str = render_to_string('documents/politica_prevension.html', ctx, request=request)
        filename = f'politica_nom035_{politica.ciclo.anio}.pdf'
        if WEASYPRINT_OK:
            pdf  = WeasyHTML(string=html_str, base_url=request.build_absolute_uri('/')).write_pdf()
            resp = HttpResponse(pdf, content_type='application/pdf')
            resp['Content-Disposition'] = f'attachment; filename="{filename}"'
        else:
            resp = HttpResponse(html_str + _PRINT_HINT, content_type='text/html; charset=utf-8')
        return resp


_PRINT_HINT = (
    '<style>#ph{position:fixed;top:0;left:0;right:0;background:#03c4ce;color:#fff;'
    'padding:10px 20px;font-family:sans-serif;font-size:13px;display:flex;'
    'align-items:center;justify-content:space-between;z-index:9999}'
    '#ph button{background:#fff;color:#03c4ce;border:none;padding:6px 16px;'
    'border-radius:99px;font-weight:700;cursor:pointer}'
    '@media print{#ph{display:none!important}}</style>'
    '<div id="ph">Vista previa &mdash; Ctrl+P para guardar como PDF'
    '<button onclick="window.print()">Imprimir / PDF</button></div>'
)
