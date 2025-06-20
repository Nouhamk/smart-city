"""
URL configuration for django_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)
from django_api.views import RegisterView, AlertListView, AlertHistoryView, AlertAcknowledgeView, AlertResolveView, UserUpdateView, UserDeleteView
from django_api.views import AlertThresholdViewSet, PredictionViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'alert-thresholds', AlertThresholdViewSet, basename='alert-threshold')
router.register(r'predictions', PredictionViewSet, basename='prediction')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/logout/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/alerts/', AlertListView.as_view(), name='alerts-list'),
    path('api/alerts/history/', AlertHistoryView.as_view(), name='alerts-history'),
    path('api/alerts/<int:pk>/acknowledge/', AlertAcknowledgeView.as_view(), name='alerts-acknowledge'),
    path('api/alerts/<int:pk>/resolve/', AlertResolveView.as_view(), name='alerts-resolve'),
    path('api/users/<int:pk>/update/', UserUpdateView.as_view(), name='user-update'),
    path('api/users/<int:pk>/delete/', UserDeleteView.as_view(), name='user-delete'),
]
urlpatterns += router.urls
