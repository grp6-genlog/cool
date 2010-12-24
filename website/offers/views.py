from django.shortcuts import render_to_response, redirect
from django.http import HttpResponseRedirect
from django import forms

from website.profiles.models import UserProfile
from website.proposals.models import Proposal
from website.requests.models import Request
from website.offers.models import Offer
from django.contrib.auth.models import User

from portobject import *
from guiutils import WaitCallbacks

import datetime, time, utils


class WaitCallbacksOffer(WaitCallbacks):
    pass    


""" 
Return an HTML page with the list of offers of the authenticated user waiting
for approval of one or the two participant.
Redirect to the home page if he isn't logged in
"""
def myoffers(request, global_address_cache=None):
    if not request.user.is_authenticated():
        return redirect('/home/')
    
    user = UserProfile.objects.get(user=request.user)
    info_offers = []
    
    for prop in user.proposal_set.all():
        new_offers = Offer.objects.filter(proposal=prop, status='P', pickup_time__gt=datetime.datetime.today())
        for of in new_offers:
            
            associated_req = of.request
            associated_offers = Offer.objects.filter(request = associated_req)
            display = True
            for other_of in associated_offers:
                if other_of.status == 'A':
                    display = False
                    break
            
            if display:
                route_points = of.proposal.routepoints_set.all()
                index_pickup = 0
                index_drop = 0
                for i in xrange(len(route_points)):
                    if route_points[i].latitude == of.pickup_point.latitude and route_points[i].longitude == of.pickup_point.longitude:
                        index_pickup = i
                    if route_points[i].latitude == of.drop_point.latitude and route_points[i].longitude == of.drop_point.longitude:
                        index_drop = i
                
                date_pick = utils.get_time_at_point([(el.latitude,el.longitude) for el in route_points],
                                                index_pickup,
                                                of.proposal.departure_time,
                                                of.proposal.arrival_time)
                
                
                date_drop = utils.get_time_at_point([(el.latitude,el.longitude) for el in route_points],
                                                index_drop,
                                                of.proposal.departure_time,
                                                of.proposal.arrival_time)
                
                
                pick_point = global_address_cache.get_address((of.pickup_point.latitude,of.pickup_point.longitude))
                drop_point = global_address_cache.get_address((of.drop_point.latitude,of.drop_point.longitude))
                infos = {
                    'driver':True, 'status':of.driver_ok, 'other':of.request.user,
                    'date_pick':date_pick, 'pick_point': pick_point,
                    'date_drop':date_drop, 'drop_point': drop_point,
                    'fee': of.total_fee, 'id':of.id, 'nb_seat': of.request.nb_requested_seats,
                }

                insert_offer(info_offers, infos)

            
    for req in user.request_set.all():
        new_offers = Offer.objects.filter(request=req, status='P', pickup_time__gt=datetime.datetime.today())
        for of in new_offers:
            associated_offers = Offer.objects.filter(request = req)
            display = True
            for other_of in associated_offers:
                if other_of.status == 'A':
                    display = False
                    break
            
            if display:
                route_points = of.proposal.routepoints_set.all()
                
                index_pickup = 0
                index_drop = 0
                for i in xrange(len(route_points)):
                    if route_points[i].latitude == of.pickup_point.latitude and route_points[i].longitude == of.pickup_point.longitude:
                        index_pickup = i
                    if route_points[i].latitude == of.drop_point.latitude and route_points[i].longitude == of.drop_point.longitude:
                        index_drop = i
                
                
                date_pick = utils.get_time_at_point([(el.latitude,el.longitude) for el in route_points],
                                                index_pickup,
                                                of.proposal.departure_time,
                                                of.proposal.arrival_time)
                
                date_drop = utils.get_time_at_point([(el.latitude,el.longitude) for el in route_points],
                                                index_drop,
                                                of.proposal.departure_time,
                                                of.proposal.arrival_time)
                
                pick_point = global_address_cache.get_address((of.pickup_point.latitude, of.pickup_point.longitude))
                drop_point = global_address_cache.get_address((of.drop_point.latitude, of.drop_point.longitude))

                infos = {
                    'driver':False, 'status':of.non_driver_ok, 'other':of.proposal.user,
                    'date_pick':date_pick, 'pick_point': pick_point,
                    'date_drop':date_drop, 'drop_point': drop_point,
                    'fee': of.total_fee, 'id':of.id, 'nb_seat': of.request.nb_requested_seats,
                }
                
                insert_offer(info_offers, infos)

    acc_bal = user.account_balance
    if WaitCallbacksOffer.message_present(request.user):
        notification = WaitCallbacksOffer.get_message(request.user)
        WaitCallbacksOffer.erase_message(request.user)
    return render_to_response('myoffers.html', locals())
    
   
    
"""
insert an instance of offer into the list sorted by status (waiting for approval
first) and then by date (earliest first)
offer_l : the current list of offer, updated after the call
new_o : the offer to insert
The instances of offer are dictionnary with at least a field 'status' and 'date_pick'
"""
def insert_offer(offer_l, new_o):
    for i in xrange(len(offer_l)):
         if (not new_o['status'] and offer_l[i]['status']):
            offer_l.insert(i,new_o)
            return
          
         elif (new_o['status'] and offer_l[i]['status']) and offer_l[i]['date_pick'] > new_o['date_pick']:
             offer_l.insert(i,new_o)
             return
         elif (not new_o['status']and not offer_l[i]['status']) and offer_l[i]['date_pick'] > new_o['date_pick']:
             offer_l.insert(i,new_o)
             return
             
    offer_l.append(new_o)
    
 

""" 
Return an HTML page with the response while trying to response to an offer
Redirect to the home page if no user is logged in or the call is invalid
If the offermanager didn't proccess the message correctly display an error
message, display a validation message otherwise.
request : request object created by django at the function call
offset : parameter set at the end of the url, represent the offer id
port_offer : port object to the offer manager
accept : true if the offer is accepted, false otherwise
@pre : /
@post : the evaluation is send to the evaluation recorder to be stored in the
    database
""" 
def responseoffer(request, offset, port_offer, accept):

    try:
        offset = int(offset)
    except:
        notification = {'content':'Invalid call', 'success':False}
        return render_to_response('home.html', locals())
    else:
    
        try:
            offer = Offer.objects.get(id=offset)
        except:
            notification = {'content':'Invalid call', 'success':False}
            return render_to_response('home.html', locals())
        else:
        
            if offer.status != 'P':
                notification = {'content':'Invalid call'+offer.status, 'success':False}
                return render_to_response('home.html', locals())
            
            if request.user != offer.proposal.user.user and request.user != offer.request.user.user:
                notification = {'content':'Invalid call', 'success':False}
                return render_to_response('error.html', locals())
                
            
            if accept:
                if request.user == offer.proposal.user.user:
                    message = "driver_agree"
                else:
                    message = "non_driver_agree"
            else:
                message = "refuseoffer"
            
            
            WaitCallbacksOffer.declare(request.user)
            
            anonymous_send_to(port_offer,(message,offer.id,offer.request.user.id,
                                           lambda:successcall(request.user),
                                           lambda(message):failurecall(request.user,message)))
            
            wait_counter = 0
            while WaitCallbacksOffer.is_pending(request.user) and wait_counter < 10:
                time.sleep(0.1)
                wait_counter += 1
            
            offer = Offer.objects.get(id=offset)
            if WaitCallbacksOffer.status(request.user) == 'success':
                if offer.status == 'A':    
                    WaitCallbacksOffer.update_message(request.user, {'content':'The ride has been confirmed','success':True})

                WaitCallbacksOffer.free(request.user)
                return redirect('/offers/')
                
            else:
                WaitCallbacksOffer.update_message(request.user , {'content':WaitCallbacksOffer.get_message(request.user),'success':False})
                    
                WaitCallbacksOffer.free(request.user)
                
                return redirect('/offers/')


"""
Success callback function
@post : update the callback dictionnary to set 'success' at the key with the user 
"""
def successcall(user, message=None):
    WaitCallbacksOffer.update(user, 'success')
  
"""
Failure callback function
@post : update the callback dictionnary to set 'fail' at the key with the user 
"""   
def failurecall(user, message=None):
    if message:
        WaitCallbacksOffer.update_message(user, message)
    WaitCallbacksOffer.update(user, 'fail')
 

