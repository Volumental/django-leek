from django.http import HttpResponse

def index(request):
    return HttpResponse('Test app', content_type='text/plain')
