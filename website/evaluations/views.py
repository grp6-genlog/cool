from django.shortcuts import render_to_response, redirect
from django.http import HttpResponseRedirect
from django import forms

from website.profiles.models import UserProfile
from website.requests.models import Request
from django.contrib.auth.models import User

from portobject import *
from guiutils import WaitCallbacks
from google_tools_json import *

import datetime, time, re



class WaitCallbacksEval(WaitCallbacks):
    pass


def myevaluations(request):
    if not request.user.is_authenticated():
        return redirect('/home/')
    
    user_p = UserProfile.objects.get(user=request.user)
    evaluation_l = Evaluation.objects.filter(user_to=user_p)
    
    return render_to_response('myevaluations.html', locals())
    
    
    
def addevaluation(request, port_evaluation=None):
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
            
            #if abs(cancellation_margin - (arrival_time - datetime.timedelta(seconds=max_delay))) < datetime.timedelta(minutes=30):
            #    form._errors["cancellation_margin"] = form.error_class(["Specify a cancellation margin earlier"])
            #    return render_to_response('requestform.html', locals())
            
            status = 'P'
            
            WaitCallbacksEval.declare(request.user)
            
            anonymous_send_to(port_request,('recordrequest',[UserID,departure_point,departure_range,
                                                            arrival_point,arrival_range,arrival_time,max_delay,
                                                            nb_requested_seats,cancellation_margin,status],
                                           successcall,
                                           failurecall,
                                           request.user))
            
            wait_counter = 0
            while WaitCallbacksEval.is_pending(request.user) and wait_counter < 10:
                time.sleep(0.1)
                wait_counter += 1
            
            if WaitCallbacksEval.status(request.user) == 'success':
                WaitCallbacksEval.free(request.user)
                notification = {'content':'Request successfully registered', 'success':True}
                return render_to_response('home.html', locals())
            else:
                print WaitCallbacksEval.status(request.user)
                WaitCallbacksEval.free(request.user)
                notification = {'content':'An error occured', 'success':False}
                return render_to_response('requestform.html', locals())
        else:
            return render_to_response('requestform.html', locals())
    else:
        form = RequestForm()
        
        return render_to_response('requestform.html', locals())


def successcall(user):
    WaitCallbacksEval.update(user, 'success')
    
def failurecall(user):
    WaitCallbacksEval.update(user, 'fail')
        
