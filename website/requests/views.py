from django.shortcuts import render_to_response, redirect
from django.http import HttpResponseRedirect
from django import forms

from website.profiles.models import UserProfile
from website.requests.models import Request
from django.contrib.auth.models import User

from portobject import PortObject

import datetime

gui_port = PortObject()


class RequestForm(forms.Form):
    departure_point_lat = forms.FloatField(label=u'Latitude departure')
    departure_point_long = forms.FloatField(label=u'Longitude departure')
    departure_range = forms.FloatField()
    arrival_point_lat = forms.FloatField(label=u'Latitude arrival')
    arrival_point_long = forms.FloatField(label=u'Longitude arrival')
    arrival_range = forms.FloatField()
    arrival_time = forms.DateTimeField(initial="yyyy-mm-dd HH:MM")
    max_delay = forms.TimeField(label=u'Maximum margin delay', initial="HH:MM")
    nb_requested_seats = forms.IntegerField(initial=1, label=u'Number of seats requested')
    cancellation_margin = forms.DateTimeField(initial="yyyy-mm-dd HH:MM")


def myrequests(request):
    if not request.user.is_authenticated():
        return redirect('/home/')
    
    user=UserProfile.objects.get(user=request.user)
    requests = user.request_set.all()
    return render_to_response('myrequests.html', locals())
    
def addrequest(request, port_request=None):
    if not request.user.is_authenticated():
        return redirect('/home/', request=request)
    
    if request.method == 'POST':
        form = RequestForm(request.POST)
        if form.is_valid():
            UserID = UserProfile.objects.get(user=request.user)
            departure_point_lat = request.POST.get('departure_point_lat', 0)
            departure_point_long = request.POST.get('departure_point_long', 0)
            departure_range = request.POST.get('departure_range', 0)
            arrival_point_lat = request.POST.get('arrival_point_lat', 0)
            arrival_point_long = request.POST.get('arrival_point_long', 0)
            arrival_range = request.POST.get('arrival_range', 0)
            arrival_time = request.POST.get('arrival_range', datetime.datetime.today())
            max_delay = request.POST.get('max_delay', datetime.datetime.today())
            nb_requested_seats = request.POST.get('nb_requested_seats', 1)
            cancellation_margin = request.POST.get('max_delay', datetime.datetime.today())
            
            port_request.send_to(gui_port,('recordrequest',[UserID,(departure_point_lat, departure_point_long),departure_range,
                                                            (arrival_point_lat, arrival_point_long),arrival_range,arrival_time,max_delay,
                                                            nb_requested_seats,cancellation_margin],
                                           successcall,
                                           failurecall))
                                           
            notification = "Success"            
        else:
            notification = "Failure"
            
        return render_to_response('requestform.html', locals())
    else:    
        form = RequestForm()
        
        return render_to_response('requestform.html', locals())


def successcall():
    print "cool"
    
def failurecall():
    print "zut"
        
    
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
