from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView
from accounts.views import LoginView, LogoutView


urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth
    path('api/v1/auth/login/', LoginView.as_view(), name='login'),
    path('api/v1/auth/logout/', LogoutView.as_view(), name='logout'),
    path('api/v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Modulos
    path('api/v1/tenants/',  include('tenants.urls')),
    path('api/v1/accounts/', include('accounts.urls')),
    path('api/v1/',          include('m00_onboarding.urls')),
    path('api/v1/',          include('m01_committee.urls')),
    path('api/v1/',          include('m02_action_plan.urls')),
    path('api/v1/',          include('m03_policy.urls')),
    path('api/v1/',          include('m04_dissemination.urls')),
    path('api/v1/',          include('m07_evidence.urls')),
    path('api/v1/',          include('m08_attendance.urls')),
    path('api/v1/',          include('notifications.urls')),
    path('api/v1/',          include('m05_questionnaires.urls')),
    path('api/v1/',          include('m06_results.urls')),
    path('api/v1/',          include('documents.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
