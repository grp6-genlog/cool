from django.shortcuts import render_to_response, redirect
from django.http import HttpResponseRedirect
from django import forms

from website.profiles.models import UserProfile
from website.requests.models import Request
from django.contrib.auth.models import User

from portobject import PortObject
from guiutils import WaitCallbacks
from google_tools_json import *

import datetime, time

gui_port = PortObject()


class RequestForm(forms.Form):
    departure_point = forms.CharField()
    departure_range = forms.FloatField()
    arrival_point = forms.CharField()
    arrival_range = forms.FloatField()
    arrival_time = forms.DateTimeField()
    max_delay = forms.TimeField(label=u'Maximum margin delay', initial="HH:MM")
    nb_requested_seats = forms.IntegerField(initial=1, label=u'Number of seats requested')
    cancellation_margin = forms.DateTimeField()


class WaitCallbacksRequest(WaitCallbacks):
    pass


def myrequests(request):
    if not request.user.is_authenticated():
        return redirect('/home/')
    
    user=UserProfile.objects.get(user=request.user)
    requests = user.request_set.all()
    request_list = []
    for req in requests:
        print json.loads(location_to_address(str(req.departure_point_lat)+","+str(req.departure_point_long)).read())['results'][0]['formatted_address']
        d = {
            'departure_point': json.loads(location_to_address(str(req.departure_point_lat)+","+str(req.departure_point_long)).read())['results'][0]['formatted_address'],
            'departure_range' : req.departure_range,
            'arrival_point' : json.loads(location_to_address(str(req.arrival_point_lat)+","+str(req.arrival_point_long)).read())['results'][0]['formatted_address'],
            'arrival_range' : req.arrival_range,
            'arrival_time': req.arrival_time,
            'max_delay': req.max_delay,
            'nb_requested_seats': req.nb_requested_seats,
            'cancellation_margin' : req.cancellation_margin,
        }
        request_list.append(d)
    return render_to_response('myrequests.html', locals())
    
def addrequest(request, port_request=None):
    if not request.user.is_authenticated():
        return redirect('/home/', request=request)

    if request.method == 'POST':
        form = RequestForm(request.POST)
        if form.is_valid():
            
            departure_point = address_to_location(request.POST.get('departure_point', 0))
            if arrival_point == -1:
                form._errors["departure_point"] = form.error_class(["No address found"])
                return render_to_response('requestform.html', locals())
                
            departure_range = request.POST.get('departure_range', 0)

            arrival_point = address_to_location(request.POST.get('arrival_point', 0))
            if arrival_point == -1:
                form._errors["arrival_point"] = form.error_class(["No address found"])
                return render_to_response('requestform.html', locals())
            
            UserID = UserProfile.objects.get(user=request.user)
            arrival_range = request.POST.get('arrival_range', 0)
            arrival_time = request.POST.get('arrival_time', datetime.datetime.today())
            max_delay = request.POST.get('max_delay', datetime.datetime.today())
            nb_requested_seats = request.POST.get('nb_requested_seats', 1)
            cancellation_margin = request.POST.get('cancellation_margin', datetime.datetime.today())
            
            WaitCallbacksRequest.declare(request.user)
            
            gui_port.send_to(port_request,('recordrequest',[UserID,departure_point,departure_range,
                                                            arrival_point,arrival_range,arrival_time,max_delay,
                                                            nb_requested_seats,cancellation_margin],
                                           successcall,
                                           failurecall,
                                           request.user))
            
            wait_counter = 0
            while WaitCallbacksRequest.is_pending(request.user) and wait_counter < 10:
                time.sleep(0.1)
                wait_counter += 1
            
            if WaitCallbacksRequest.status(request.user) == 'success':
                WaitCallbacksRequest.free(request.user)
                return render_to_response('home.html', locals())
            else:
                print WaitCallbacksRequest.status(request.user)
                WaitCallbacksRequest.free(request.user)
                return render_to_response('error.html', locals())
        else:
            return render_to_response('requestform.html', locals())
    else:
        form = RequestForm()
        
        return render_to_response('requestform.html', locals())



def successcall(user):
    WaitCallbacksRequest.update(user, 'success')
    
def failurecall(user):
    WaitCallbacksRequest.update(user, 'fail')
        
    
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
