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
        self.tracker_port = Tracker(get_port(self.user_notif_port))
        self.ride_port = RideManager(get_port(self.user_notif_port), get_port(self.tracker_port), get_port(self.payment_port), get_port(self.evaluation_port))
        self.offer_port = OfferManager(get_port(self.user_notif_port), get_port(self.ride_port))
        self.find_pair_port = FindPair(get_port(self.offer_port))
        self.proposal_rec_port = ProposalRecorder(get_port(self.find_pair_port))
        self.request_rec_port = RequestRecorder(get_port(self.find_pair_port))
        
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
    (r'^register/$', 'register', {'port_profile':global_ports.get_e()}),
    (r'^profile/$', 'editprofile'),
)

urlpatterns += patterns('website.requests.views',
    (r'^requests/$', 'myrequests'),
    (r'^addrequest/$', 'addrequest', {'port_request':global_ports.get_request()}),
    (r'^editrequest/(\d+)/$', 'editrequest'),
)
