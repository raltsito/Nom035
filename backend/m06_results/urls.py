from rest_framework.routers import DefaultRouter
from .views import ResultadoViewSet

router = DefaultRouter()
router.register('resultados', ResultadoViewSet, basename='resultado')

urlpatterns = router.urls
