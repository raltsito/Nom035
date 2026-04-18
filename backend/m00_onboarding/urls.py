from rest_framework.routers import DefaultRouter
from .views import TrabajadorViewSet, CicloNOMViewSet

router = DefaultRouter()
router.register('trabajadores', TrabajadorViewSet, basename='trabajador')
router.register('ciclos', CicloNOMViewSet, basename='ciclo')

urlpatterns = router.urls
