from django.http import HttpResponse
from django.template.loader import render_to_string
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.permissions import IsTenantAdmin
from .models import Reunion, Asistente
from .serializers import ReunionSerializer, AsistenteSerializer

try:
    from weasyprint import HTML as WeasyHTML
    WEASYPRINT_OK = True
except Exception:
    WEASYPRINT_OK = False


def _wrap(data, meta=None, errors=None, code=status.HTTP_200_OK):
    return Response({'data': data, 'meta': meta or {}, 'errors': errors}, status=code)


class ReunionViewSet(viewsets.ModelViewSet):
    permission_classes = (IsTenantAdmin,)
    serializer_class   = ReunionSerializer

    def get_queryset(self):
        qs       = Reunion.objects.filter(
            tenant=self.request.user.tenant
        ).select_related('ciclo').prefetch_related('asistentes')
        ciclo_id = self.request.query_params.get('ciclo_id')
        tipo     = self.request.query_params.get('tipo')
        if ciclo_id:
            qs = qs.filter(ciclo_id=ciclo_id)
        if tipo:
            qs = qs.filter(tipo=tipo)
        return qs

    def list(self, request, *args, **kwargs):
        from django.db.models import Count
        qs      = self.get_queryset()
        resumen = (
            qs.values('tipo').annotate(count=Count('id'))
        )
        return _wrap(
            ReunionSerializer(qs, many=True).data,
            meta={
                'count':    qs.count(),
                'por_tipo': {r['tipo']: r['count'] for r in resumen},
            },
        )

    def retrieve(self, request, *args, **kwargs):
        return _wrap(ReunionSerializer(self.get_object()).data)

    def create(self, request, *args, **kwargs):
        serializer = ReunionSerializer(data=request.data)
        if serializer.is_valid():
            obj = serializer.save(tenant=request.user.tenant)
            return _wrap(ReunionSerializer(obj).data, code=status.HTTP_201_CREATED)
        return _wrap(None, errors=serializer.errors, code=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial    = kwargs.pop('partial', False)
        instance   = self.get_object()
        serializer = ReunionSerializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            obj = serializer.save()
            return _wrap(ReunionSerializer(obj).data)
        return _wrap(None, errors=serializer.errors, code=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()
        return _wrap(None)

    @action(detail=True, methods=['get'], url_path='acta')
    def acta(self, request, pk=None):
        reunion  = self.get_object()
        from m00_onboarding.models import CicloNOM
        ciclo    = reunion.ciclo
        ctx = {
            'tenant':    request.user.tenant,
            'ciclo':     ciclo,
            'reunion':   reunion,
            'asistentes': reunion.asistentes.all(),
        }
        html_str = render_to_string('documents/acta_reunion.html', ctx, request=request)
        filename = f'acta_reunion_{reunion.fecha}_{reunion.id}.pdf'
        if WEASYPRINT_OK:
            pdf  = WeasyHTML(string=html_str, base_url=request.build_absolute_uri('/')).write_pdf()
            resp = HttpResponse(pdf, content_type='application/pdf')
            resp['Content-Disposition'] = f'attachment; filename="{filename}"'
        else:
            resp = HttpResponse(html_str + _PRINT_HINT, content_type='text/html; charset=utf-8')
        return resp


class AsistenteViewSet(viewsets.ModelViewSet):
    permission_classes = (IsTenantAdmin,)
    serializer_class   = AsistenteSerializer
    http_method_names  = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        return Asistente.objects.filter(tenant=self.request.user.tenant).select_related('reunion')

    def create(self, request, *args, **kwargs):
        reunion_id = request.data.get('reunion')
        if not Reunion.objects.filter(id=reunion_id, tenant=request.user.tenant).exists():
            return _wrap(None, errors={'reunion': ['No encontrada.']}, code=404)
        serializer = AsistenteSerializer(data=request.data)
        if serializer.is_valid():
            a = serializer.save(tenant=request.user.tenant)
            return _wrap(AsistenteSerializer(a).data, code=status.HTTP_201_CREATED)
        return _wrap(None, errors=serializer.errors, code=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial    = kwargs.pop('partial', False)
        instance   = self.get_object()
        serializer = AsistenteSerializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            a = serializer.save()
            return _wrap(AsistenteSerializer(a).data)
        return _wrap(None, errors=serializer.errors, code=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()
        return _wrap(None)


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
