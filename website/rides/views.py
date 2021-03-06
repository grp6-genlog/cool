from django.shortcuts import render_to_response, redirect
from django.http import HttpResponseRedirect
from django import forms

from website.profiles.models import UserProfile
from website.proposals.models import Proposal
from website.requests.models import Request
from website.offers.models import Offer
from website.rides.models import Ride
from django.contrib.auth.models import User


from portobject import *
from guiutils import WaitCallbacks

import datetime, time, utils


class WaitCallbacksRide(WaitCallbacks):
    pass
                      

""" 
Return an HTML page with the list of rides of the authenticated user that are
associated to a pending request or proposal and that the offer is not pending or discarded
Redirect to the home page if he isn't logged in
"""
def myrides(request, global_address_cache=None):
    
    if not request.user.is_authenticated():
        return redirect('/home/')        
    
    user = UserProfile.objects.get(user=request.user)
    info_rides = []
    
    three_days_ago = datetime.datetime.today() - datetime.timedelta(days=3)
    for prop in Proposal.objects.filter(user=user, status='P', departure_time__gt=three_days_ago):
        
        ol1 = Offer.objects.filter(proposal=prop, status='A') # every future offer accepted by both where the user is the driver
        ol2 = Offer.objects.filter(proposal=prop, status='F') # every offer finished where the user is the driver
        ol3 = Offer.objects.filter(proposal=prop, status='C') # every offer cancelled where the user is the driver
        offer_list = ol1 | ol2 | ol3
        for of in offer_list:
            
            ride = Ride.objects.filter(offer=of)
            
            if len(ride) == 1:
                ride = ride[0]
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
                    'driver':True, 'other':of.request.user,
                    'date_pick':date_pick, 'pick_point': pick_point,
                    'date_drop':date_drop, 'drop_point': drop_point,
                    'fee': of.total_fee, 'id':ride.id,
                    'nb_seat': of.request.nb_requested_seats, 'status':of.status
                }

                insert_ride(info_rides, infos)
                


    for req in Request.objects.filter(user=user, status='P', arrival_time__gt=three_days_ago):
        
        ol1 = Offer.objects.filter(request=req, status='A') # every future offer accepted by both where the user is the passenger
        ol2 = Offer.objects.filter(request=req, status='F') # every offer finished where the user is the passenger
        ol3 = Offer.objects.filter(request=req, status='C') # every offer cancelled where the user is the passenger
        offer_list = ol1 | ol2 | ol3
        for of in offer_list:
            ride = Ride.objects.filter(offer=of)    
    
            if len(ride) == 1:
                ride = ride[0]
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
                    'driver':False, 'other':of.proposal.user,
                    'date_pick':date_pick, 'pick_point': pick_point,
                    'date_drop':date_drop, 'drop_point': drop_point,
                    'fee': of.total_fee, 'id':ride.id,
                    'nb_seat': of.request.nb_requested_seats, 'status':of.status
                }

                insert_ride(info_rides, infos)
       
    if WaitCallbacksRide.message_present(request.user):
        notification = WaitCallbacksRide.get_message(user)
        WaitCallbacksRide.erase_message(user)
    return render_to_response('myrides.html', locals())
    
    
"""
insert an instance of ride into the list sorted by status (waiting for approval
first) and then by date (earliest first)
ride_l : the current list of offer, updated after the call
new_r : the ride to insert
The instances of ride are dictionnary with at least a field 'status' and 'date_pick'
"""  
def insert_ride(ride_l, new_r):
    for i in xrange(len(ride_l)):
         if ride_l[i]['date_pick'] > new_r['date_pick']:
             ride_l.insert(i,new_r)
             return
             
    ride_l.append(new_r)
    

""" 
Return an HTML page with the response while trying to cancel a ride
Redirect to the home page if no user is logged in or the call is invalid
If the ridemanager didn't proccess the message correctly display an error
message, display a validation message otherwise.
request : request object created by django at the function call
offset : parameter set at the end of the url, represent the ride id
ride_port : port object to the ride manager
@pre : /
@post : the response is send to the ride manager to update the database
"""
def cancelride(request, offset, ride_port):

    try:
        offset = int(offset)
    except:
        notification = {'content':'Invalid call, not a ride', 'success':False}
        return render_to_response('home.html', locals())
    else:
    
        try:
            ride = Ride.objects.get(id=offset)
        except:
            notification = {'content':'Invalid call, no ride corresponding', 'success':False}
            return render_to_response('home.html', locals())
        else:
        
            if ride.offer.status != 'A':
                notification = {'content':'Invalid call, ride not agreed', 'success':False}
                return render_to_response('home.html', locals())
            
            if request.user != ride.offer.proposal.user.user and request.user != ride.offer.request.user.user:
                notification = {'content':'Invalid call', 'success':False}
                return render_to_response('home.html', locals())
                
            message = "cancelride"            
            
            WaitCallbacksRide.declare(request.user)
            
            up = UserProfile.objects.get(user=request.user)
            anonymous_send_to(ride_port,(message,ride.id,
                                           lambda:successcall(request.user),
                                           lambda:failurecall(request.user)))
            
            wait_counter = 0
            while WaitCallbacksRide.is_pending(request.user) and wait_counter < 10:
                time.sleep(0.1)
                wait_counter += 1
            
            ride = Ride.objects.get(id=offset)
            if WaitCallbacksRide.status(request.user) == 'success':
                WaitCallbacksRide.free(request.user)
                if ride.offer.status == 'C':
                    WaitCallbacksRide.update_message(request.user, {'content':'The ride has been cancelled','success':True})

                return redirect('/rides/')
                
            else:
                WaitCallbacksRide.free(request.user)
                
                return redirect('/rides/')


"""
Success callback function
@post : update the callback dictionnary to set 'success' at the key with the user 
"""        
def successcall(user, message=None):
    WaitCallbacksRide.update(user, 'success')

"""
Failure callback function
@post : update the callback dictionnary to set 'fail' at the key with the user 
"""   
def failurecall(user, message=None):
    if message:
        WaitCallbacksRide.update_message(user, message)
    WaitCallbacksRide.update(user, 'fail')

