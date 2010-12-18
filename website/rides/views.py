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
    Display the list of rides of the authenticated user
    If he isn't connected, display the home page
"""
def myrides(request, global_address_cache=None):
    
    if not request.user.is_authenticated():
        return redirect('/home/')        
    
    user = UserProfile.objects.get(user=request.user)
    info_rides = []
    
    for prop in Proposal.objects.filter(user=user, status='P', departure_time__gt=datetime.datetime.today()):
        
        offer_list = Offer.objects.filter(proposal=prop, status='A') # every future offer accepted by both where the user is the driver
        for of in offer_list:
            print of.id
            ride = Ride.objects.get(offer=of)
            
            route_points = of.proposal.routepoints_set.all()
            index_pickup = 0
            index_drop = 0
            for i in xrange(len(route_points)):
                if route_points[i].latitude == of.pickup_point_lat and route_points[i].longitude == of.pickup_point_long:
                    index_pickup = i
                if route_points[i].latitude == of.drop_point_lat and route_points[i].longitude == of.drop_point_long:
                    index_drop = i
            
            date_pick = utils.get_time_at_point([(el.latitude,el.longitude) for el in route_points],
                                            index_pickup,
                                            of.proposal.departure_time,
                                            of.proposal.arrival_time)
            
            date_drop = utils.get_time_at_point([(el.latitude,el.longitude) for el in route_points],
                                            index_drop,
                                            of.proposal.departure_time,
                                            of.proposal.arrival_time)
            
            
            pick_point = global_address_cache.get_address((of.pickup_point_lat, of.pickup_point_long))
            drop_point = global_address_cache.get_address((of.drop_point_lat, of.drop_point_long))
            
            infos = {
                'driver':True, 'other':of.request.user,
                'date_pick':date_pick, 'pick_point': pick_point,
                'date_drop':date_drop, 'drop_point': drop_point,
                'fee': of.total_fee, 'id':ride.id, 'nb_seat': of.request.nb_requested_seats
            }

            insert_ride(info_rides, infos)


    for req in Request.objects.filter(user=user, status='P', arrival_time__gt=datetime.datetime.today()):
        
        offer_list = Offer.objects.filter(request=req, status='A') # every future offer accepted by both where the user is the non-driver
        for of in offer_list:
            ride = Ride.objects.get(offer=of)    
            
            route_points = of.proposal.routepoints_set.all()
            
            index_pickup = 0
            index_drop = 0
            for i in xrange(len(route_points)):
                if route_points[i].latitude == of.pickup_point_lat and route_points[i].longitude == of.pickup_point_long:
                    index_pickup = i
                if route_points[i].latitude == of.drop_point_lat and route_points[i].longitude == of.drop_point_long:
                    index_drop = i
            
            
            date_pick = utils.get_time_at_point([(el.latitude,el.longitude) for el in route_points],
                                            index_pickup,
                                            of.proposal.departure_time,
                                            of.proposal.arrival_time)
            
            date_drop = utils.get_time_at_point([(el.latitude,el.longitude) for el in route_points],
                                            index_drop,
                                            of.proposal.departure_time,
                                            of.proposal.arrival_time)
            
            pick_point = global_address_cache.get_address((of.pickup_point_lat,of.pickup_point_long))
            drop_point = global_address_cache.get_address((of.drop_point_lat,of.drop_point_long))
            
            infos = {
                'driver':False, 'other':of.proposal.user,
                'date_pick':date_pick, 'pick_point': pick_point,
                'date_drop':date_drop, 'drop_point': drop_point,
                'fee': of.total_fee, 'id':ride.id, 'nb_seat': of.request.nb_requested_seats
            }

            insert_ride(info_rides, infos)
    
    if WaitCallbacksRide.message_present(request.user):
        notification = WaitCallbacksRide.get_message(user)
        WaitCallbacksRide.erase_message(user)
    return render_to_response('myrides.html', locals())
    
    
    
def insert_ride(offer_l, new_o):
    for i in xrange(len(offer_l)):
         if offer_l[i]['date_pick'] > new_o['date_pick']:
             offer_l.insert(i,new_o)
             return
             
    offer_l.append(new_o)
    
 
"""
    Response to an offer
    offer : the id of the offer specified in the url
    port_offer : the port_object to the offer manager
    accept : boolean containing the response
    global_address_cache : cache address for optimisation
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
                return render_to_response('error.html', locals())
                
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
                print WaitCallbacksRide.status(request.user)
                WaitCallbacksRide.free(request.user)
                
                return redirect('/rides/')


        
def successcall(user, message=None):
    WaitCallbacksRide.update(user, 'success')
    
def failurecall(user, message=None):
    if message:
        WaitCallbacksRide.update_message(user, message)
    WaitCallbacksRide.update(user, 'fail')

