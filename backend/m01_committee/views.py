from django.http import HttpResponse
from django.template.loader import render_to_string
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.permissions import IsTenantAdmin
from .models import ComiteNOM, MiembroComite, CapacitacionDC3
from .serializers import ComiteNOMSerializer, MiembroComiteSerializer, CapacitacionDC3Serializer

try:
    from weasyprint import HTML as WeasyHTML
    WEASYPRINT_OK = True
except Exception:
    WEASYPRINT_OK = False


def _wrap(data, meta=None, errors=None, code=status.HTTP_200_OK):
    return Response({'data': data, 'meta': meta or {}, 'errors': errors}, status=code)


class ComiteViewSet(viewsets.ModelViewSet):
    permission_classes = (IsTenantAdmin,)
    serializer_class   = ComiteNOMSerializer

    def get_queryset(self):
        qs = ComiteNOM.objects.filter(
            tenant=self.request.user.tenant
        ).prefetch_related('miembros__capacitaciones').select_related('ciclo')
        ciclo_id = self.request.query_params.get('ciclo_id')
        if ciclo_id:
            qs = qs.filter(ciclo_id=ciclo_id)
        return qs

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        return _wrap(ComiteNOMSerializer(qs, many=True).data, meta={'count': qs.count()})

    def retrieve(self, request, *args, **kwargs):
        return _wrap(ComiteNOMSerializer(self.get_object()).data)

    def create(self, request, *args, **kwargs):
        serializer = ComiteNOMSerializer(data=request.data)
        if serializer.is_valid():
            comite = serializer.save(tenant=request.user.tenant)
            return _wrap(
                ComiteNOMSerializer(comite).data,
                code=status.HTTP_201_CREATED,
            )
        return _wrap(None, errors=serializer.errors, code=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = ComiteNOMSerializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            comite = serializer.save()
            return _wrap(ComiteNOMSerializer(comite).data)
        return _wrap(None, errors=serializer.errors, code=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()
        return _wrap(None)

    @action(detail=True, methods=['get'], url_path='acta')
    def acta(self, request, pk=None):
        comite   = self.get_object()
        miembros = comite.miembros.filter(activo=True)
        ctx = {
            'tenant':   request.user.tenant,
            'comite':   comite,
            'miembros': miembros,
        }
        html_str = render_to_string('documents/acta_comite.html', ctx, request=request)
        filename = f'acta_comite_nom035_{comite.ciclo.anio}.pdf'
        if WEASYPRINT_OK:
            pdf = WeasyHTML(
                string=html_str, base_url=request.build_absolute_uri('/')
            ).write_pdf()
            resp = HttpResponse(pdf, content_type='application/pdf')
            resp['Content-Disposition'] = f'attachment; filename="{filename}"'
        else:
            resp = HttpResponse(html_str + _PRINT_HINT, content_type='text/html; charset=utf-8')
        return resp


class MiembroViewSet(viewsets.ModelViewSet):
    permission_classes = (IsTenantAdmin,)
    serializer_class   = MiembroComiteSerializer

    def get_queryset(self):
        qs = MiembroComite.objects.filter(
            tenant=self.request.user.tenant
        ).prefetch_related('capacitaciones')
        comite_id = self.request.query_params.get('comite_id')
        if comite_id:
            qs = qs.filter(comite_id=comite_id)
        return qs

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        return _wrap(MiembroComiteSerializer(qs, many=True).data, meta={'count': qs.count()})

    def retrieve(self, request, *args, **kwargs):
        return _wrap(MiembroComiteSerializer(self.get_object()).data)

    def create(self, request, *args, **kwargs):
        # Validate comite belongs to same tenant
        comite_id = request.data.get('comite')
        if not ComiteNOM.objects.filter(id=comite_id, tenant=request.user.tenant).exists():
            return _wrap(None, errors={'comite': ['Comite no encontrado.']}, code=400)
        serializer = MiembroComiteSerializer(data=request.data)
        if serializer.is_valid():
            miembro = serializer.save(tenant=request.user.tenant)
            return _wrap(
                MiembroComiteSerializer(miembro).data,
                code=status.HTTP_201_CREATED,
            )
        return _wrap(None, errors=serializer.errors, code=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = MiembroComiteSerializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            miembro = serializer.save()
            return _wrap(MiembroComiteSerializer(miembro).data)
        return _wrap(None, errors=serializer.errors, code=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()
        return _wrap(None)


class CapacitacionViewSet(viewsets.ModelViewSet):
    permission_classes = (IsTenantAdmin,)
    serializer_class   = CapacitacionDC3Serializer
    http_method_names  = ['get', 'post', 'delete', 'head', 'options']

    def get_queryset(self):
        qs = CapacitacionDC3.objects.filter(tenant=self.request.user.tenant)
        miembro_id = self.request.query_params.get('miembro_id')
        if miembro_id:
            qs = qs.filter(miembro_id=miembro_id)
        return qs

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        return _wrap(CapacitacionDC3Serializer(qs, many=True).data, meta={'count': qs.count()})

    def create(self, request, *args, **kwargs):
        miembro_id = request.data.get('miembro')
        if not MiembroComite.objects.filter(id=miembro_id, tenant=request.user.tenant).exists():
            return _wrap(None, errors={'miembro': ['Miembro no encontrado.']}, code=400)
        serializer = CapacitacionDC3Serializer(data=request.data)
        if serializer.is_valid():
            dc3 = serializer.save(tenant=request.user.tenant)
            return _wrap(CapacitacionDC3Serializer(dc3).data, code=status.HTTP_201_CREATED)
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
    '<div id="ph">Vista previa del acta &mdash; para guardar como PDF usa Ctrl+P'
    '<button onclick="window.print()">Imprimir / PDF</button></div>'
)
