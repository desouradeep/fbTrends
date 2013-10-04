from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from extract_data import collect

def index(request):
    if request.method == 'POST' and request.is_ajax() == True:
        collecter = collect(access_token=request.POST['access_token'])
        print 'Access Token Recieved'
        collecter.start()

    context = RequestContext(request, {
        'header' : 'hello world',
        })
    return render_to_response('index.html', context_instance=context)