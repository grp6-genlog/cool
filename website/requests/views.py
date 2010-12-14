from django.shortcuts import render_to_response, redirect
from django.http import HttpResponseRedirect
from django import forms

from website.profiles.models import UserProfile
from website.requests.models import Request
from django.contrib.auth.models import User


class RequestForm(forms.form):
    departure_point_lat = forms.FloatField(label=u'Latitude departure')
    departure_point_long = forms.FloatField(label=u'Longitude departure')
    departure_range = forms.FloatField()
    arrival_point_lat = forms.FloatField(label=u'Latitude arrival')
    arrival_point_long = forms.FloatField(label=u'Longitude arrival')
    arrival_range = forms.FloatField()
    arrival_time = forms.DateTimeField()
    max_delay = forms.DateTimeField(label=u'Maximum delay of ')
    nb_requested_seats = forms.IntegerField(default=1, label=u'Number of seats requested')
    cancellation_margin = forms.DateTimeField()


def myrequests(request):
    if not request.user.is_authenticated():
        return redirect('/home/')
    
    user=UserProfile.objects.get(user=request.user)
    requests = user.request_set.all()
    return render_to_response('myrequests.html', locals())
    
def addrequest(request):
    if not request.user.is_authenticated():
        return redirect('/home/', request=request)
        
    form = RequestForm()
    
    return render_to_response('requestform.html', locals())
    
    
def editrequest(request, offset):
    try:
        offset = int(offset)
    except ValueError:
        raise Http404()
    
    try:
        req = Request.object.get(id=offset)
    except:
        error_msg = "No request found"
        return render_to_response('error.html', locals())
    return render_to_response('home.html', locals())
