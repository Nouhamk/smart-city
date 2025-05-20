import csv
import io
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from app.cron import import_openmeteo_data
from app.supabase_client import supabase

def get_data(request):
    table_name = request.GET.get('table', 'normalized_data')
    response = supabase.table(table_name).select('*').execute()
    data = response.data
    return JsonResponse(data, safe=False)

@csrf_exempt
def upload_csv_to_table(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)

    table_name = request.GET.get('table', 'normalized_data')

    if 'file' not in request.FILES:
        return JsonResponse({'error': 'No CSV file found in the request'}, status=400)

    csv_file = request.FILES['file']

    if not csv_file.name.endswith('.csv'):
        return JsonResponse({'error': 'Uploaded file is not a CSV'}, status=400)

    try:
        file_data = csv_file.read().decode('utf-8')

        #print(f"File data preview: {file_data[:100]}") #For debugging

        csv_data = csv.DictReader(io.StringIO(file_data))

        #print(f"CSV headers: {csv_data.fieldnames}") #For debugging

        # Convert CSV data to a list of dictionaries
        rows = []
        for row in csv_data:
            # Remove empty strings and convert to None
            processed_row = {k: (v if v != '' else None) for k, v in row.items()}
            rows.append(processed_row)

        if not rows:
            return JsonResponse({'error': 'CSV file is empty'}, status=400)

        #print(f"First row data: {rows[0]}") # For debugging

        response = supabase.table(table_name).insert(rows).execute()

        return JsonResponse({
            'message': f'Successfully uploaded {len(rows)} rows to {table_name}',
            'data': response.data
        })

    except Exception as e:
        #import traceback #for debugging
        #print(f"Error processing CSV upload: {str(e)}") #for debugging
        #print(traceback.format_exc()) #for debugging
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt #might have to change this for role-based access control
def trigger_import(request):
    if request.method == 'POST':
        try:
            result = import_openmeteo_data()
            if result:
                return JsonResponse({'status': 'success', 'message': 'Weather data import completed successfully'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Weather data import failed'}, status=500)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Only POST method allowed'}, status=405)