import mimetypes
import os

from django.http import FileResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from accounts.permissions import IsTenantAdmin
from .models import EvidenciaDocumento
from .serializers import EvidenciaDocumentoSerializer


def _wrap(data, meta=None, errors=None, code=status.HTTP_200_OK):
    return Response({'data': data, 'meta': meta or {}, 'errors': errors}, status=code)


class EvidenciaViewSet(viewsets.ModelViewSet):
    permission_classes = (IsTenantAdmin,)
    serializer_class   = EvidenciaDocumentoSerializer
    parser_classes     = (MultiPartParser, FormParser)
    http_method_names  = ['get', 'post', 'delete', 'head', 'options']

    def get_queryset(self):
        qs       = EvidenciaDocumento.objects.filter(
            tenant=self.request.user.tenant
        ).select_related('ciclo', 'subido_por')
        ciclo_id = self.request.query_params.get('ciclo_id')
        modulo   = self.request.query_params.get('modulo')
        if ciclo_id:
            qs = qs.filter(ciclo_id=ciclo_id)
        if modulo:
            qs = qs.filter(modulo=modulo)
        return qs

    def list(self, request, *args, **kwargs):
        from django.db.models import Count, Sum
        qs      = self.get_queryset()
        resumen = (
            qs.values('modulo')
              .annotate(count=Count('id'), total_bytes=Sum('tamanio'))
        )
        return _wrap(
            EvidenciaDocumentoSerializer(qs, many=True, context={'request': request}).data,
            meta={
                'count':       qs.count(),
                'total_bytes': sum(e.tamanio for e in qs),
                'por_modulo':  {r['modulo']: r['count'] for r in resumen},
            },
        )

    def retrieve(self, request, *args, **kwargs):
        return _wrap(
            EvidenciaDocumentoSerializer(self.get_object(), context={'request': request}).data
        )

    def create(self, request, *args, **kwargs):
        archivo = request.FILES.get('archivo')
        if not archivo:
            return _wrap(None, errors={'archivo': ['Requerido.']}, code=400)

        serializer = EvidenciaDocumentoSerializer(
            data=request.data, context={'request': request}
        )
        if serializer.is_valid():
            mime, _ = mimetypes.guess_type(archivo.name)
            ev = serializer.save(
                tenant      = request.user.tenant,
                subido_por  = request.user,
                tamanio     = archivo.size,
                tipo_mime   = mime or 'application/octet-stream',
            )
            return _wrap(
                EvidenciaDocumentoSerializer(ev, context={'request': request}).data,
                code=status.HTTP_201_CREATED,
            )
        return _wrap(None, errors=serializer.errors, code=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.archivo:
            try:
                os.remove(instance.archivo.path)
            except (FileNotFoundError, OSError):
                pass
        instance.delete()
        return _wrap(None)

    @action(detail=True, methods=['get'], url_path='download')
    def download(self, request, pk=None):
        ev = self.get_object()
        if not ev.archivo:
            return _wrap(None, errors={'archivo': ['No hay archivo asociado.']}, code=404)
        try:
            response = FileResponse(
                open(ev.archivo.path, 'rb'),
                content_type=ev.tipo_mime or 'application/octet-stream',
            )
            filename = os.path.basename(ev.archivo.name)
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        except (FileNotFoundError, OSError):
            return _wrap(None, errors={'archivo': ['Archivo no encontrado en servidor.']}, code=404)
