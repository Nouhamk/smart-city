from django.urls import path, include

from data_api.routes import DataView, PredictionView

app_name = 'data_api'

urlpatterns = [
    path('api/data/', DataView.as_view(), name='get_data'),
    path('api/prediction/', PredictionView.as_view(), name='get_predictions'),
    path('', include('data_api.weather_index.urls')),
]