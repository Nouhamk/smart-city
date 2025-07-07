from django.urls import path

from data_api.routes import DataView

app_name = 'data_api'

urlpatterns = [
    path('api/data', DataView.as_view(), name='get_data'),
]