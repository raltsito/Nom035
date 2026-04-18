from django.urls import path
from .views import generar_informe

urlpatterns = [
    path('documentos/informe-nom035/', generar_informe, name='informe-nom035'),
]
