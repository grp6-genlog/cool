from django.shortcuts import render_to_response, redirect
from django.http import HttpResponseRedirect
from django import forms

from website.profiles.models import UserProfile
from website.requests.models import Request
from website.offers.models import Offer
from django.contrib.auth.models import User

from portobject import *
from guiutils import WaitCallbacks
from google_tools_json import *

import datetime, time, re


""" Different fields to record a new request """
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

""" 
Return an HTML page with the list of requests of the authenticated user that
are still pending and in the future
Redirect to the home page if he isn't logged in
"""
def myrequests(request):
    if not request.user.is_authenticated():
        return redirect('/home/')
    
    user=UserProfile.objects.get(user=request.user)
    requests = Request.objects.filter(user=user, status='P', arrival_time__gt=datetime.datetime.today())
    request_list = []
    for req in requests:
        offer_l = Offer.objects.filter(request = req)
        display = True
        if len(offer_l) > 0:
            for of in offer_l:
                if of.status != 'P' and of.status != 'D':
                    display = False
    
        if display:
            d = {
                'departure_point': json.loads(location_to_address(str(req.departure_point_lat)+","+str(req.departure_point_long)).read())['results'][0]['formatted_address'],
                'departure_range' : req.departure_range,
                'arrival_point' : json.loads(location_to_address(str(req.arrival_point_lat)+","+str(req.arrival_point_long)).read())['results'][0]['formatted_address'],
                'arrival_range' : req.arrival_range,
                'arrival_time': req.arrival_time,
                'max_delay': str(req.max_delay/3600)+":"+str((req.max_delay % 3660) / 60),
                'nb_requested_seats': req.nb_requested_seats,
                'cancellation_margin' : req.cancellation_margin,
                'id' : req.id,
            }
            request_list.append(d)
    return render_to_response('myrequests.html', locals())
    
    
""" 
Return an HTML page with the response while trying to add a request
Redirect to the home page if no user is logged in or the call is invalid
If request.POST is false, display the empty request form
If the request form is not filled correctly, display an message explaining
the error.
If the request recorder didn't proccess the message correctly display an error
message, display a validation message otherwise.
request : request object created by django at the function call
port_request : port object to the request recorder
@pre : /
@post : the request is send to the request recorder to be stored in the
    database
"""     
def addrequest(request, port_request=None):
    if not request.user.is_authenticated():
        return redirect('/home/', request=request)

    if request.method == 'POST':
        form = RequestForm(request.POST)
        if form.is_valid():
            form.cleaned_data
            
            departure_point = address_to_location(form.cleaned_data['departure_point'])
            if departure_point == -1:
                form._errors["departure_point"] = form.error_class(["No address found"])
                return render_to_response('requestform.html', locals())
                
            departure_range = request.POST.get('departure_range', 0)

            arrival_point = address_to_location(form.cleaned_data['arrival_point'])
            if arrival_point == -1:
                form._errors["arrival_point"] = form.error_class(["No address found"])
                return render_to_response('requestform.html', locals())
            
            arrival_time = form.cleaned_data['arrival_time']
            UserID = UserProfile.objects.get(user=request.user)
            
            if arrival_time < datetime.datetime.today():
                form._errors["arrival_time"] = form.error_class(["Arrival time already passed"])
                return render_to_response('requestform.html', locals())
                
            arrival_range = form.cleaned_data['arrival_range']
                        
            max_delay = form.cleaned_data['max_delay']
            max_delay = int(max_delay.hour*3600 + max_delay.minute * 60)
            nb_requested_seats = form.cleaned_data['nb_requested_seats']
            cancellation_margin = form.cleaned_data['cancellation_margin']
            
            status = 'P'
            
            WaitCallbacksRequest.declare(request.user)
            
            anonymous_send_to(port_request,('recordrequest',[UserID,departure_point,departure_range,
                                                            arrival_point,arrival_range,arrival_time,max_delay,
                                                            nb_requested_seats,cancellation_margin,status],
                                           successcall,
                                           failurecall,
                                           request.user))
            
            wait_counter = 0
            while WaitCallbacksRequest.is_pending(request.user) and wait_counter < 10:
                time.sleep(0.1)
                wait_counter += 1
            
            if WaitCallbacksRequest.status(request.user) == 'success':
                WaitCallbacksRequest.free(request.user)
                notification = {'content':'Request successfully registered', 'success':True}
                return render_to_response('home.html', locals())
            else:
                print WaitCallbacksRequest.status(request.user)
                WaitCallbacksRequest.free(request.user)
                notification = {'content':'An error occured', 'success':False}
                return render_to_response('requestform.html', locals())
        else:
            return render_to_response('requestform.html', locals())
    else:
        init = {
            'arrival_time' : datetime.datetime.today(),
            'cancellation_margin' : datetime.datetime.today(),
            'max_delay' : '00:30'
        }
        form = RequestForm(initial = init)
        
        return render_to_response('requestform.html', locals())


""" 
Return an HTML page with the response while trying to cancel a request
Redirect to the home page if no user is logged in or the call is invalid
If the offermanager didn't proccess the message correctly display an error
message, display a validation message otherwise.
request : request object created by django at the function call
offset : parameter set at the end of the url, represent the request id
port_offer : port object to the offer manager
@pre : /
@post : the response is send to the offer manager to update the database
"""
def cancelrequest(request, offset, port_offer=None):
    try:
        offset = int(offset)
    except ValueError:
        notification = {'content':'Invalid call, not a request', 'success':False}
        return render_to_response('home.html', locals())
    
    try:
        req = Request.objects.get(id=offset)
    except:
        notification = {'content':'Invalid call, request does not exist', 'success':False}
        return render_to_response('home.html', locals())
        
    if req.user.user != request.user:
        notification = {'content':'Invalid call, permission denied', 'success':False}
        return render_to_response('home.html', locals())
        
    if req.status != 'P' or req.cancellation_margin < datetime.datetime.today():
        notification = {'content':'Too late to cancel', 'success':False}
        return render_to_response('home.html', locals())

    
    WaitCallbacksRequest.declare(request.user)
                    
    anonymous_send_to(port_offer,('cancelrequest', offset,
                                            lambda:successcall(request.user),
                                            lambda:failurecall(request.user)))
                    
    wait_counter = 0
    while WaitCallbacksRequest.is_pending(request.user) and wait_counter < 10:
        time.sleep(0.1)
        wait_counter += 1
                    
    if WaitCallbacksRequest.status(request.user) == 'success':
        WaitCallbacksRequest.free(request.user)
        notification = {'content':'Request canceled', 'success':True}
        return render_to_response('home.html', locals())
    else:
        print WaitCallbacksRequest.status(request.user)
        WaitCallbacksRequest.free(request.user)
        notification = {'content':'An error occured, try again later', 'success':False}
        return render_to_response('home.html', locals())


"""
Success callback function
@post : update the callback dictionnary to set 'success' at the key with the user 
"""
def successcall(user):
    WaitCallbacksRequest.update(user, 'success')

"""
Failure callback function
@post : update the callback dictionnary to set 'fail' at the key with the user 
"""    
def failurecall(user):
    WaitCallbacksRequest.update(user, 'fail')
        
