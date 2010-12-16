from django.shortcuts import render_to_response, redirect
from django.http import HttpResponseRedirect
from django import forms

from website.profiles.models import UserProfile
from website.offers.models import Proposal
from website.requests.models import Request
from django.contrib.auth.models import User


from portobject import PortObject
from guiutils import WaitCallbacks
form google_tools_json import *

import datetime, time

gui_port = PortObject()


class WaitCallbacksOffer(WaitCallbacks):
    pass


def myoffers(request):
    if not request.user.is_authenticated():
        return redirect('/home/')
    
    user=UserProfile.objects.get(user=request.user)
    info_offers = []
    
    for prop in user.proposal_set.all():
        new_offers = Offer.objects.filter(proposal=prop, status='Pending')
        for of in new_offers:
            route_points = of.proposal.routepoints_set.all()
            
            date_pick = get_time(of.proposal.departure_time,
                                 of.proposal.arrival_time,
                                 route_points,
                                (of.pickup_point_lat, of.pickup_point_long))
            
            date_drop = get_time(of.proposal.departure_time,
                                 of.proposal.arrival_time,
                                 route_points,
                                (of.drop_point_lat, of.drop_point_long))
            pick_point = ""
            drop_point = ""
            
            infos = {
                'driver':True, 'status':of.driver_ok, 'other':of.request.user,
                'date_pick':date_pick, 'pick_point': pick_point,
                'date_drop':date_drop, 'drop_point': drop_point,
                'fee': of.total_fee, 'id':of.id
            }
            
            self.insert_offer(info_offers, infos)
            
    for req in user.request_set.all()
        new_offers = Offer.objects.filter(request=req, status='Pending')
        for of in new_offers:
            route_points = of.proposal.routepoints_set.all()
            
            date_pick = get_time(of.proposal.departure_time,
                                 of.proposal.arrival_time,
                                 route_points,
                                (of.pickup_point_lat, of.pickup_point_long))
            
            date_drop = get_time(of.proposal.departure_time,
                                 of.proposal.arrival_time,
                                 route_points,
                                (of.drop_point_lat, of.drop_point_long))
            pick_point = ""
            drop_point = ""
            
            infos = {
                'driver':False, 'status':of.non_driver_ok, 'other':of.proposal.user,
                'date_pick':date_pick, 'pick_point': pick_point,
                'date_drop':date_drop, 'drop_point': drop_point,
                'fee': of.total_fee, 'id':of.id
            }
            
            self.insert_offer(info_offers, infos)
    
    return render_to_response('myproposals.html', locals())
    
    
    
def insert_offer(offer_l, new_o):
    for i in xrange(len(offer_l)):
         if offer_l[i]['date_pick'] > new_o['date_pick']:
             rp_list.insert(i,new_o)
             break
    
    
def get_time(dep_time, arr_time, checkpoints, pick_point):
    points_str = []
    cpt_point = 0
    for point in checkpoints:
        points_str.append(str(point.latitude)+","+str(point.longitude))
        if point.latitude == pick_point[0] and point.longitude == pick_point[1]:
            point_index = cpt_point
        cpt_point += 1
        
    distance = distance_origin_dest(points_str[0], points_str[-1], points_str[1:-1])
    total_time = (dep_time - arr_time).seconds + (dep_time - arr_time).days*60*60*24
    
    time_per_point = total_time / (len(checkpoints)-1)
    
    return datetime.timedelta(seconds=(time_per_point * point_index)) + dep_time
    
    
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



def editproposal(request, port_request=None):
    if not request.user.is_authenticated():
        return redirect('/home/', request=request)

    if request.method == 'POST':
        form = RequestForm(request.POST)
        
        if form.is_valid():
            form.cleaned_data
            
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
            
            WaitCallbacksRequest.declare(request.user)
            
            gui_port.send_to(port_request,('recordrequest',[UserID,(departure_point_lat, departure_point_long),departure_range,
                                                            (arrival_point_lat, arrival_point_long),arrival_range,arrival_time,max_delay,
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
        user=UserProfile.objects.get(user=request.user)
        init = {
            'car_id':user.car_id,
            'car_description':user.car_description,
            'number_of_seats':user.number_of_seats,
            'money_per_km':user.money_per_km,
        }
          
        form = ProposalForm(initial=init)

        return render_to_response('requestform.html', locals())
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
