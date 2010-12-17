from django.shortcuts import render_to_response, redirect
from django.http import HttpResponseRedirect
from django import forms

from website.profiles.models import UserProfile
from website.proposals.models import Proposal
from website.requests.models import Request
from website.offers.models import Offer
from website.rides.models import Ride
from django.contrib.auth.models import User


from portobject import PortObject
from guiutils import WaitCallbacks
from google_tools_json import *

import datetime, time

gui_port = PortObject()


class WaitCallbacksRide(WaitCallbacks):
    pass    

                      

def myrides(request):
    if not request.user.is_authenticated():
        return redirect('/home/')
    
    user=UserProfile.objects.get(user=request.user)
    info_rides = []
    
    for prop in user.proposal_set.all():
        new_offers = Offer.objects.filter(proposal=prop, status='A')
        for of in new_offers:
            ride = Ride.objects.filter(offer=of)
            if ride:
                route_points = of.proposal.routepoints_set.all()
                
                date_pick = get_time(of.proposal.departure_time,
                                     of.proposal.arrival_time,
                                     route_points,
                                    (of.pickup_point_lat, of.pickup_point_long))
                
                date_drop = get_time(of.proposal.departure_time,
                                     of.proposal.arrival_time,
                                     route_points,
                                    (of.drop_point_lat, of.drop_point_long))
                                    
                pick_point_js = json.loads(location_to_address(str(of.pickup_point_lat)+","+str(of.pickup_point_long)).read())
                if len(pick_point_js)==0:
                    pick_point = "No address"
                else:
                    pick_point = pick_point_js['results'][0]['formatted_address']
                drop_point_js = json.loads(location_to_address(str(of.drop_point_lat)+","+str(of.drop_point_long)).read())
                if len(drop_point_js)==0:
                    drop_point = "No address"
                else:
                    drop_point = drop_point_js['results'][0]['formatted_address']
                
                infos = {
                    'driver':True, 'status':of.driver_ok, 'other':of.request.user,
                    'date_pick':date_pick, 'pick_point': pick_point,
                    'date_drop':date_drop, 'drop_point': drop_point,
                    'fee': of.total_fee, 'id':ride.id, 'nb_seat': of.request.nb_requested_seats
                }
                
                self.insert_ride(info_ride, infos)
            
    for req in user.request_set.all():
        new_offers = Offer.objects.filter(request=req, status='A')
        for of in new_offers:
            ride = Ride.objects.filter(request=of)
            if ride:
                route_points = of.proposal.routepoints_set.all()
                
                date_pick = get_time(of.proposal.departure_time,
                                     of.proposal.arrival_time,
                                     route_points,
                                    (of.pickup_point_lat, of.pickup_point_long))
                
                date_drop = get_time(of.proposal.departure_time,
                                     of.proposal.arrival_time,
                                     route_points,
                                    (of.drop_point_lat, of.drop_point_long))
                
                pick_point_js = json.loads(location_to_address(str(of.pickup_point_lat)+","+str(of.pickup_point_long)).read())
                if len(pick_point_js)==0:
                    pick_point = "No address"
                else:
                    pick_point = pick_point_js['results'][0]['formatted_address']
                drop_point_js = json.loads(location_to_address(str(of.drop_point_lat)+","+str(of.drop_point_long)).read())
                if len(drop_point_js)==0:
                    drop_point = "No address"
                else:
                    drop_point = drop_point_js['results'][0]['formatted_address']
                
                infos = {
                    'driver':False, 'status':of.non_driver_ok, 'other':of.proposal.user,
                    'date_pick':date_pick, 'pick_point': pick_point,
                    'date_drop':date_drop, 'drop_point': drop_point,
                    'fee': of.total_fee, 'id':ride.id
                }
                
                self.insert_ride(info_rides, infos)
    
    
    notification = WaitCallbacksOffer.get_message(user)
    WaitCallbacksOffer.erase_message(user)
    return render_to_response('myrides.html', locals())
    
    
    
def insert_ride(ride_l, new_o):
    for i in xrange(len(ride_l)):
         if ride_l[i]['date_pick'] > new_o['date_pick']:
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
    

def responseoffer(request, offset, port_offer, accept):

    try:
        offset = int(offset)
    except:
        notification = {'content':'Invalid call', 'success':False}
        return render_to_response('myproposals.html', locals())
    else:
    
        try:
            offer = Offer.objects.get(id=offset)
        except:
            notification = {'content':'Invalid call', 'success':False}
            return render_to_response('myproposals.html', locals())
        else:
        
            if offer.status != 'P':
                notification = {'content':'Invalid call', 'success':False}
                return render_to_response('myproposals.html', locals())
            
            if request.user != offer.proposal.user and request.user != offer.request.user:
                notification = {'content':'Invalid call', 'success':False}
                return render_to_response('myproposals.html', locals())
            
            if accept:
                if request.user == offer.proposal.user:
                    message = "driveragree"
                else:
                    message = "nondriveragree"
            else:
                message = "refuseoffer"
            
            WaitCallbacksOffer.declare(request.user)
            
            gui_port.send_to(port_offer,(message,offer.id,
                                           successcall,
                                           failurecall,
                                           request.user))
            
            wait_counter = 0
            while WaitCallbacksOffer.is_pending(request.user) and wait_counter < 10:
                time.sleep(0.1)
                wait_counter += 1
            
            if WaitCallbacksOffer.status(request.user) == 'success':
                WaitCallbacksOffer.free(request.user)
                
                return redirect('/offers/')
                
            else:
                print WaitCallbacksOffer.status(request.user)
                WaitCallbacksOffer.free(request.user)
                
                
                return redirect('/offers/')


        
def successcall(user, message=None):
    WaitCallbacksOffer.update(user, 'success')
    
def failurecall(user, message=None):
    if message:
        WaitCallbacksOffer.update_message(user, message)
    WaitCallbacksOffer.update(user, 'fail')
        
    
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
