from django.http import JsonResponse
from .supabase_client import supabase

def get_data(request):
    table_name = request.GET.get('table', 'normalized_data')
    response = supabase.table(table_name).select('*').execute()
    data = response.data
    return JsonResponse(data, safe=False)