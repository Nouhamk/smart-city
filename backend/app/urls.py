"""
URL configuration for backend project.

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
from django.urls import path
from app.metricsview import get_data, upload_csv_to_table, trigger_import

app_name = 'app'

urlpatterns = [
    path('get-data', get_data, name='get_data'),
    path('upload-csv', upload_csv_to_table, name='upload_csv'),
    path('admin/csv/trigger-import', trigger_import, name='trigger_import'),
]
