from django.shortcuts import render_to_response, redirect
from django.http import HttpResponseRedirect
from django import forms

from website.profiles.models import UserProfile
from website.requests.models import Request
from django.contrib.auth.models import User

from portobject import PortObject

import datetime, time, threading

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


class WaitCallbacksProfile():
    _active = {}
    _active_lock = threading.Lock()
    
    @classmethod
    def append(cls, u):
        with cls._active_lock:
            cls._active.update({u:'pending'})
    
    @classmethod
    def is_pending(cls, u):
        with cls._active_lock:
            if u in cls._active:
                return cls._active.get(u) == 'pending'
            else:
                return False
            
    @classmethod
    def declare(cls, u):
        with cls._active_lock:
            while u in cls._active:
                pass
            cls._active.update({u:'pending'})
            
    @classmethod
    def free(cls, u):
        with cls._active_lock:
            if u in cls._active:
                cls._active.pop(u)

    @classmethod
    def update(cls, u, status):
        with cls._active_lock:
            cls._active.update({u:status})
            
            
    @classmethod
    def status(cls, u):
        with cls._active_lock:
            if u in cls._active:
                return cls._active.get(u)
            else:
                return None


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
            arrival_time = request.POST.get('arrival_time', datetime.datetime.today())
            max_delay = request.POST.get('max_delay', datetime.datetime.today())
            nb_requested_seats = request.POST.get('nb_requested_seats', 1)
            cancellation_margin = request.POST.get('cancellation_margin', datetime.datetime.today())
            
            WaitCallbacksProfile.declare(request.user)
            
            print [UserID,(departure_point_lat, departure_point_long),departure_range,(arrival_point_lat, arrival_point_long),arrival_range,arrival_time,max_delay,nb_requested_seats,cancellation_margin]
            
            gui_port.send_to(port_request,('recordrequest',[UserID,(departure_point_lat, departure_point_long),departure_range,
                                                            (arrival_point_lat, arrival_point_long),arrival_range,arrival_time,max_delay,
                                                            nb_requested_seats,cancellation_margin],
                                           successcall,
                                           failurecall,
                                           request.user))
            
            wait_counter = 0
            while WaitCallbacksProfile.is_pending(request.user) and wait_counter < 20:
                time.sleep(0.1)
                wait_counter += 1
            
            if WaitCallbacksProfile.status(request.user) == 'success':
                WaitCallbacksProfile.free(request.user)
                return render_to_response('home.html', locals())
            else:
                print WaitCallbacksProfile.status(request.user)
                WaitCallbacksProfile.free(request.user)
                return render_to_response('error.html', locals())
        else:
            return render_to_response('requestform.html', locals())
    else:    
        form = RequestForm()
        
        return render_to_response('requestform.html', locals())


def successcall(user):
    print "cool"
    WaitCallbacksProfile.update(user, 'success')
    
def failurecall(user):
    print "zut"
    WaitCallbacksProfile.update(user, 'fail')
        
    
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
