from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenBlacklistView,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from django_api.views import (
    RegisterView, LoginView, AlertListView, AlertHistoryView,
    AlertAcknowledgeView, AlertResolveView, UserUpdateView, UserDeleteView,
    AlertThresholdViewSet, AlertThresholdDetailView,
    RegionListView
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Authentication
    path('api/auth/login/', LoginView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/logout/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('api/auth/register/', RegisterView.as_view(), name='register'),

    # Alerts
    path('api/alerts/', AlertListView.as_view(), name='alerts-list'),
    path('api/alerts/history/', AlertHistoryView.as_view(), name='alerts-history'),
    path('api/alerts/<int:pk>/acknowledge/', AlertAcknowledgeView.as_view(), name='alerts-acknowledge'),
    path('api/alerts/<int:pk>/resolve/', AlertResolveView.as_view(), name='alerts-resolve'),

    # Users
    path('api/users/<int:pk>/update/', UserUpdateView.as_view(), name='user-update'),
    path('api/users/<int:pk>/delete/', UserDeleteView.as_view(), name='user-delete'),

    # Alert Thresholds
    path('api/alert-thresholds/', AlertThresholdViewSet.as_view(), name='alert-thresholds-list'),
    path('api/alert-thresholds/<int:pk>/', AlertThresholdDetailView.as_view(), name='alert-thresholds-detail'),

    # Regions
    path('api/regions/', RegionListView.as_view(), name='regions-list'),

    # Data
    path('', include('data_api.urls'))
]