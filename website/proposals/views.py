from django.shortcuts import render_to_response, redirect
from django import forms

from website.profiles.models import UserProfile
from website.proposals.models import Proposal, RoutePoints
from django.contrib.auth.models import User

from portobject import PortObject
from guiutils import WaitCallbacks

import datetime, time

gui_port = PortObject()


class ProposalForm(forms.Form):

    car_id = forms.CharField(max_length=50)
    car_description = forms.CharField(max_length=500,
                            widget=forms.Textarea,
                            required=False)
    number_of_seats = forms.IntegerField()
    money_per_km = forms.FloatField()
    departure_time = forms.DateTimeField()
    arrival_time = forms.DateTimeField()

class WaitCallbacksProposal(WaitCallbacks):
    pass


def myproposals(request):
    if not request.user.is_authenticated():
        return redirect('/home/')
    
    user=UserProfile.objects.get(user=request.user)
    proposals = user.proposal_set.all()
    return render_to_response('myproposals.html', locals())
    
    
def addproposal(request, port_proposal=None):
    if not request.user.is_authenticated():
        return redirect('/home/', request=request)

    if request.method == 'POST':
        form = ProposalForm(request.POST)
        
        if form.is_valid():
            form.cleaned_data
            
            UserID = UserProfile.objects.get(user=request.user)
            car_id = form.cleaned_data['car_id']
            car_description = form.cleaned_data['car_description']
            number_of_seats = form.cleaned_data['number_of_seats']
            money_per_km = form.cleaned_data['money_per_km']
            departure_time = form.cleaned_data['departure_time']
            arrival_time = form.cleaned_data['arrival_time']
            
            WaitCallbacksProposal.declare(request.user)
            
            gui_port.send_to(port_proposal,('recordproposal',[UserID,[],car_description,car_id,
                                                            number_of_seats,money_per_km,departure_time,arrival_time],
                                           successcall,
                                           failurecall,
                                           request.user))
            
            wait_counter = 0
            while WaitCallbacksProposal.is_pending(request.user) and wait_counter < 10:
                time.sleep(0.1)
                wait_counter += 1
            
            if WaitCallbacksProposal.status(request.user) == 'success':
                WaitCallbacksProposal.free(request.user)
                return render_to_response('home.html', locals())
            else:
                print WaitCallbacksProposal.status(request.user)
                WaitCallbacksProposal.free(request.user)
                return render_to_response('error.html', locals())
        else:
            return render_to_response('proposalform.html', locals())
    else:
        
        user=UserProfile.objects.get(user=request.user)
        init = {
            'car_id':user.car_id,
            'car_description':user.car_description,
            'number_of_seats':user.number_of_seats,
            'money_per_km':user.money_per_km,
            'departure_time':datetime.datetime.today().strftime("%Y-%m-%d %H:%M"),
            'arrival_time':datetime.datetime.today().strftime("%Y-%m-%d %H:%M"),
        }
          
        form = ProposalForm(initial=init)
        
        return render_to_response('proposalform.html', locals())


        
def successcall(user):
    WaitCallbacksProposal.update(user, 'success')
    
def failurecall(user):
    WaitCallbacksProposal.update(user, 'fail')
        
    
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
