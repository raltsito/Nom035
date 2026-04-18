from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MeView, ChangePasswordView, UserViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')

urlpatterns = [
    path('me/', MeView.as_view(), name='me'),
    path('me/change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('', include(router.urls)),
]
