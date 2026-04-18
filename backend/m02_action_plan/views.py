from django.http import HttpResponse
from django.template.loader import render_to_string
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.permissions import IsTenantAdmin
from .models import PlanAccion, AccionMedida
from .serializers import PlanAccionSerializer, AccionMedidaSerializer

try:
    from weasyprint import HTML as WeasyHTML
    WEASYPRINT_OK = True
except Exception:
    WEASYPRINT_OK = False


def _wrap(data, meta=None, errors=None, code=status.HTTP_200_OK):
    return Response({'data': data, 'meta': meta or {}, 'errors': errors}, status=code)


class PlanAccionViewSet(viewsets.ModelViewSet):
    permission_classes = (IsTenantAdmin,)
    serializer_class   = PlanAccionSerializer

    def get_queryset(self):
        qs = PlanAccion.objects.filter(
            tenant=self.request.user.tenant
        ).select_related('ciclo').prefetch_related('acciones')
        ciclo_id = self.request.query_params.get('ciclo_id')
        if ciclo_id:
            qs = qs.filter(ciclo_id=ciclo_id)
        return qs

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        return _wrap(PlanAccionSerializer(qs, many=True).data, meta={'count': qs.count()})

    def retrieve(self, request, *args, **kwargs):
        return _wrap(PlanAccionSerializer(self.get_object()).data)

    def create(self, request, *args, **kwargs):
        serializer = PlanAccionSerializer(data=request.data)
        if serializer.is_valid():
            plan = serializer.save(tenant=request.user.tenant)
            return _wrap(PlanAccionSerializer(plan).data, code=status.HTTP_201_CREATED)
        return _wrap(None, errors=serializer.errors, code=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial  = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = PlanAccionSerializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            plan = serializer.save()
            return _wrap(PlanAccionSerializer(plan).data)
        return _wrap(None, errors=serializer.errors, code=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()
        return _wrap(None)

    @action(detail=True, methods=['get'], url_path='reporte')
    def reporte(self, request, pk=None):
        plan     = self.get_object()
        acciones = plan.acciones.all()
        ctx = {
            'tenant':   request.user.tenant,
            'plan':     plan,
            'acciones': acciones,
            'stats':    PlanAccionSerializer(plan).data['stats'],
        }
        html_str = render_to_string('documents/plan_accion.html', ctx, request=request)
        filename = f'plan_accion_nom035_{plan.ciclo.anio}.pdf'
        if WEASYPRINT_OK:
            pdf  = WeasyHTML(string=html_str, base_url=request.build_absolute_uri('/')).write_pdf()
            resp = HttpResponse(pdf, content_type='application/pdf')
            resp['Content-Disposition'] = f'attachment; filename="{filename}"'
        else:
            resp = HttpResponse(html_str + _PRINT_HINT, content_type='text/html; charset=utf-8')
        return resp


class AccionMedidaViewSet(viewsets.ModelViewSet):
    permission_classes = (IsTenantAdmin,)
    serializer_class   = AccionMedidaSerializer

    def get_queryset(self):
        qs = AccionMedida.objects.filter(tenant=self.request.user.tenant)
        plan_id  = self.request.query_params.get('plan_id')
        estado   = self.request.query_params.get('estado')
        if plan_id:
            qs = qs.filter(plan_id=plan_id)
        if estado:
            qs = qs.filter(estado=estado)
        return qs

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        return _wrap(AccionMedidaSerializer(qs, many=True).data, meta={'count': qs.count()})

    def retrieve(self, request, *args, **kwargs):
        return _wrap(AccionMedidaSerializer(self.get_object()).data)

    def create(self, request, *args, **kwargs):
        plan_id = request.data.get('plan')
        if not PlanAccion.objects.filter(id=plan_id, tenant=request.user.tenant).exists():
            return _wrap(None, errors={'plan': ['Plan no encontrado.']}, code=400)
        serializer = AccionMedidaSerializer(data=request.data)
        if serializer.is_valid():
            accion = serializer.save(tenant=request.user.tenant)
            return _wrap(AccionMedidaSerializer(accion).data, code=status.HTTP_201_CREATED)
        return _wrap(None, errors=serializer.errors, code=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial  = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = AccionMedidaSerializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            accion = serializer.save()
            return _wrap(AccionMedidaSerializer(accion).data)
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
    '<div id="ph">Vista previa del plan &mdash; Ctrl+P para guardar como PDF'
    '<button onclick="window.print()">Imprimir / PDF</button></div>'
)
