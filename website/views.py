from django.shortcuts import render_to_response
from django.http import HttpResponse
from django import forms

import datetime

class PasswordForm(forms.Form):
    password = forms.CharField(label=(u''),
                       max_length=50,
                       widget=forms.PasswordInput(render_value=True),
                       error_messages={'required': 'si tu mets rien ca marchera pas'}) 


def home(request):
    current_date = datetime.datetime.now()
    form = PasswordForm()
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

