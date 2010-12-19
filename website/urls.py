from django.conf.urls.defaults import *
from django.conf import settings

from django.contrib.auth.views import logout
 
from django.contrib import admin
admin.autodiscover()


import os, sys    
sys.path.insert(0, os.path.join(settings.PROJECT_PATH,'modules'))

from profilerecorder import ProfileRecorder
from proposalrecorder import ProposalRecorder
from requestrecorder import RequestRecorder
from findpair import FindPair
from offermanager import OfferManager
from ridemanager import RideManager
from paymentmanager import PaymentManager
from evaluationmanager import EvaluationManager
from usernotifier import UserNotifier
from tracker import Tracker
import guiutils

class PortObjects(object):

    def __init__(self):
        print "starting objects"
        self.profile_rec_port = ProfileRecorder().get_port()
        self.user_notif_port = UserNotifier().get_port()
        self.payment_port = PaymentManager().get_port()
        self.evaluation_port = EvaluationManager().get_port()
        self.tracker_port = None#Tracker(self.user_notif_port).get_port()
        self.ride_port = RideManager(self.user_notif_port, self.tracker_port, self.payment_port, self.evaluation_port).get_port()
        self.offer_port = OfferManager(self.user_notif_port, self.ride_port).get_port()
        self.find_pair_port = FindPair(self.offer_port).get_port()
        self.proposal_rec_port = ProposalRecorder(self.find_pair_port).get_port()
        self.request_rec_port = RequestRecorder(self.find_pair_port).get_port()
        

global_ports = PortObjects()
global_address_cache = guiutils.AddressCache()
global_address_cache.load('addresses.cache')


urlpatterns = patterns('',
    (r'^media_f/(.*)$', 'django.views.static.serve', { 'document_root': settings.MEDIA_ROOT }),
    (r'^img_f/(.*)$', 'django.views.static.serve', { 'document_root': settings.IMAGE_ROOT }),
    (r'^css_f/(.*)$', 'django.views.static.serve', { 'document_root': settings.CSS_ROOT }),
    
    (r'^admin/', include(admin.site.urls)),
    (r'^my_admin/jsi18n', 'django.views.i18n.javascript_catalog'),
)

urlpatterns += patterns('website.views',
    (r'^$', 'home'),
    (r'^home/$', 'home'),
    (r'^logout/$', 'logout'),
)

urlpatterns += patterns('website.profiles.views',
    (r'^register/$', 'register', {'port_profile':global_ports.profile_rec_port}),
    (r'^profile/$', 'editprofile', {'port_profile':global_ports.profile_rec_port}),
    (r'^profile/(?P<offset>\d+)/$', 'publicprofile'),
    (r'^password/$', 'changepassword', {'port_profile':global_ports.profile_rec_port}),
    (r'^account/$', 'myaccount', {'port_payment':global_ports.payment_port,}),
    (r'^emptyaccount/$', 'emptyaccount', {'port_payment':global_ports.payment_port,}),
)

urlpatterns += patterns('website.requests.views',
    (r'^requests/$', 'myrequests'),
    (r'^addrequest/$', 'addrequest', {'port_request':global_ports.request_rec_port}),
    (r'^cancelrequest/(?P<offset>\d+)/$', 'cancelrequest', {'port_offer':global_ports.offer_port}),
)

urlpatterns += patterns('website.proposals.views',
    (r'^proposals/$', 'myproposals'),
    (r'^addproposal/$', 'addproposal', {'port_proposal':global_ports.proposal_rec_port,'global_address_cache':global_address_cache}),
    (r'^cancelproposal/(?P<offset>\d+)/$', 'cancelproposal', {'port_offer':global_ports.offer_port}),
)

urlpatterns += patterns('website.offers.views',
    (r'^offers/$', 'myoffers',{'global_address_cache':global_address_cache}),
    (r'^acceptoffer/(?P<offset>\d+)/$', 'responseoffer', {'port_offer':global_ports.offer_port,'accept':True}),
    (r'^discardoffer/(?P<offset>\d+)/$', 'responseoffer', {'port_offer':global_ports.offer_port,'accept':False}),
)

urlpatterns += patterns('website.rides.views',
    (r'^rides/$', 'myrides', {'global_address_cache':global_address_cache}),
    (r'^cancelride/(?P<offset>\d+)/$', 'cancelride', {'ride_port':global_ports.ride_port,}),
)

urlpatterns += patterns('website.evaluations.views',
    (r'^evaluations/$', 'myevaluations'),
    (r'^addevaluation/(?P<offset>\d+)/$', 'addevaluation', {'port_evaluation':global_ports.evaluation_port,}),
)

