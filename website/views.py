from django.shortcuts import render_to_response

from django.http import HttpResponse

import datetime

def home(request):
    current_date = datetime.datetime.now()
    return render_to_response('index.html', locals())
    
def hello(request):
    return render_to_response('hello.html', locals())

def current_datetime(request):
    current_date = datetime.datetime.now()
    return render_to_response('current_datetime.html', locals())


def hours_ahead(request, offset):
    try:
        offset = int(offset)
    except ValueError:
        raise Http404()
    dt = datetime.datetime.now() + datetime.timedelta(hours=offset)
    html = "<html><body>In %s hour(s), it will be %s.</body></html>" % (offset, dt)
    return HttpResponse(html)

