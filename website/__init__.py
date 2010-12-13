import sys, os

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.append(os.path.join(PROJECT_PATH,'modules'))

#from portobject import PortObject
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
        self.tracker_port = Tracker(self.user_notif_port)
        self.ride_port = RideManager(self.user_notif_port, self.tracker_port, self.payment_port, self.evaluation_port)
        self.offer_port = OfferManager(self.user_notif_port, self.ride_port)
        self.find_pair_port = FindPair(self.offer_port)
        self.proposal_rec_port = ProposalRecorder(self.find_pair_port)
        self.request_rec_port = RequestRecorder(self.find_pair_port)
    
     
    """ designed by Oren Tirosh and Jeff Pitman """
    def __new__(self, *args, **kwargs):
        if not '_singleton' in self.__dict__:
            print "first time created"
            slate = object.__new__(self)
            slate.state = {
                 'threads':True,
                 # add other state things as required
            }
            self._singleton = slate
        return self._singleton 

#PortObjects()

class singleton(object):
     """ designed by Oren Tirosh and Jeff Pitman """
     def __new__(self, *args, **kwargs):
         print "new singleton"
         if not '_singleton' in self.__dict__:
            print "first time created"
            slate = object.__new__(self)
            slate.state = {
                'threads':True,
                # add other state things as required
            }
            self._singleton = slate
         return self._singleton

singleton()
print "Car Pooling Server is now runing"

