from django.urls import path
from .routes import WeatherIndexView, WeatherIndexHistoryView, WeatherIndexConfigView

app_name = 'weather_index'

urlpatterns = [
    path('api/weather-index/', WeatherIndexView.as_view(), name='weather_index'),
    path('api/weather-index/history/', WeatherIndexHistoryView.as_view(), name='weather_index_history'),
    path('api/weather-index/config/', WeatherIndexConfigView.as_view(), name='weather_index_config'),
] 