from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PoliticaViewSet

router = DefaultRouter()
router.register('politica', PoliticaViewSet, basename='politica')

urlpatterns = [
    path('', include(router.urls)),
]
