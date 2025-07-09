from django.urls import path
from .routes import (
    WeatherIndexView, 
    WeatherIndexHistoryView, 
    WeatherIndexConfigView,
    WeatherIndexCurrentView,
    WeatherIndexAlertsView
)

app_name = 'weather_index'

urlpatterns = [
    # Endpoints pour l'indice météo
    path('api/weather-index/', WeatherIndexView.as_view(), name='weather_index'),
    path('api/weather-index/history/', WeatherIndexHistoryView.as_view(), name='weather_index_history'),
    path('api/weather-index/config/', WeatherIndexConfigView.as_view(), name='weather_index_config'),
    path('api/weather-index/current/', WeatherIndexCurrentView.as_view(), name='weather_index_current'),
    path('api/weather-index/alerts/', WeatherIndexAlertsView.as_view(), name='weather_index_alerts'),
] 