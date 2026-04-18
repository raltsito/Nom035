from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReunionViewSet, AsistenteViewSet

router = DefaultRouter()
router.register('reuniones',  ReunionViewSet,   basename='reuniones')
router.register('asistentes', AsistenteViewSet, basename='asistentes')

urlpatterns = [
    path('', include(router.urls)),
]
