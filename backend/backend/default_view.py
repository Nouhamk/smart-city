from django.http import HttpResponse

def default_view(request):
    return HttpResponse("Welcome to the API root!")
