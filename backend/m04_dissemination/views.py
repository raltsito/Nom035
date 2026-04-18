from django.http import HttpResponse
from django.template.loader import render_to_string
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.permissions import IsTenantAdmin
from .models import ActividadDifusion
from .serializers import ActividadDifusionSerializer

try:
    from weasyprint import HTML as WeasyHTML
    WEASYPRINT_OK = True
except Exception:
    WEASYPRINT_OK = False


def _wrap(data, meta=None, errors=None, code=status.HTTP_200_OK):
    return Response({'data': data, 'meta': meta or {}, 'errors': errors}, status=code)


class ActividadDifusionViewSet(viewsets.ModelViewSet):
    permission_classes = (IsTenantAdmin,)
    serializer_class   = ActividadDifusionSerializer

    def get_queryset(self):
        qs       = ActividadDifusion.objects.filter(
            tenant=self.request.user.tenant
        ).select_related('ciclo')
        ciclo_id = self.request.query_params.get('ciclo_id')
        tipo     = self.request.query_params.get('tipo')
        if ciclo_id:
            qs = qs.filter(ciclo_id=ciclo_id)
        if tipo:
            qs = qs.filter(tipo=tipo)
        return qs

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        # Resumen por tipo para el header
        from django.db.models import Count, Sum
        resumen = (
            qs.values('tipo')
              .annotate(count=Count('id'), participantes=Sum('num_participantes'))
        )
        total_participantes = sum(r['num_participantes'] or 0 for r in qs.values('num_participantes'))
        return _wrap(
            ActividadDifusionSerializer(qs, many=True).data,
            meta={
                'count':              qs.count(),
                'total_participantes': total_participantes,
                'por_tipo':           {r['tipo']: r['count'] for r in resumen},
            },
        )

    def retrieve(self, request, *args, **kwargs):
        return _wrap(ActividadDifusionSerializer(self.get_object()).data)

    def create(self, request, *args, **kwargs):
        serializer = ActividadDifusionSerializer(data=request.data)
        if serializer.is_valid():
            act = serializer.save(tenant=request.user.tenant)
            return _wrap(ActividadDifusionSerializer(act).data, code=status.HTTP_201_CREATED)
        return _wrap(None, errors=serializer.errors, code=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial  = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = ActividadDifusionSerializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            act = serializer.save()
            return _wrap(ActividadDifusionSerializer(act).data)
        return _wrap(None, errors=serializer.errors, code=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()
        return _wrap(None)

    @action(detail=False, methods=['get'], url_path='reporte')
    def reporte(self, request):
        ciclo_id = request.query_params.get('ciclo_id')
        if not ciclo_id:
            return _wrap(None, errors={'ciclo_id': ['Requerido.']}, code=400)

        from m00_onboarding.models import CicloNOM
        try:
            ciclo = CicloNOM.objects.get(id=ciclo_id, tenant=request.user.tenant)
        except CicloNOM.DoesNotExist:
            return _wrap(None, errors={'ciclo_id': ['No encontrado.']}, code=404)

        qs = self.get_queryset().filter(ciclo=ciclo)
        ctx = {
            'tenant':      request.user.tenant,
            'ciclo':       ciclo,
            'actividades': qs,
            'total':       qs.count(),
            'total_part':  sum(a.num_participantes for a in qs),
        }
        html_str = render_to_string('documents/difusion.html', ctx, request=request)
        filename = f'difusion_nom035_{ciclo.anio}.pdf'
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
    '<div id="ph">Vista previa &mdash; Ctrl+P para PDF'
    '<button onclick="window.print()">Imprimir / PDF</button></div>'
)
