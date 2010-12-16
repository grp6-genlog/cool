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

class PortObjects(object):

    def __init__(self):
        self.profile_rec_port = ProfileRecorder()
        self.user_notif_port = UserNotifier()
        self.payment_port = PaymentManager()
        self.evaluation_port = EvaluationManager()
        self.tracker_port = Tracker(self.get_port(self.user_notif_port))
        self.ride_port = RideManager(self.get_port(self.user_notif_port), self.get_port(self.tracker_port), self.get_port(self.payment_port), self.get_port(self.evaluation_port))
        self.offer_port = OfferManager(self.get_port(self.user_notif_port), self.get_port(self.ride_port))
        self.find_pair_port = FindPair(self.get_port(self.offer_port))
        self.proposal_rec_port = ProposalRecorder(self.get_port(self.find_pair_port))
        self.request_rec_port = RequestRecorder(self.get_port(self.find_pair_port))
        
    def get_port(self, port):
        return port.get_port()
    

global_ports = PortObjects()

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
    (r'^hello/$','hello'),
    (r'^logout/$', 'logout'),
)

urlpatterns += patterns('website.profiles.views',
    (r'^register/$', 'register', {'port_profile':global_ports.profile_rec_port.get_port()}),
    (r'^profile/$', 'editprofile', {'port_profile':global_ports.profile_rec_port.get_port()}),
)

urlpatterns += patterns('website.requests.views',
    (r'^requests/$', 'myrequests'),
    (r'^addrequest/$', 'addrequest', {'port_request':global_ports.request_rec_port.get_port()}),
    (r'^editrequest/(\d+)/$', 'editrequest'),
)
