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

profile_rec_port = ProfileRecorder()
user_notif_port = UserNotifier()
payment_port = PaymentManager()
evaluation_port = EvaluationManager()
tracker_port = Tracker(user_notif_port)
ride_port = RideManager(user_notif_port, tracker_port, payment_port, evaluation_port)
offer_port = OfferManager(user_notif_port, ride_port)
find_pair_port = FindPair(offer_port)
proposal_rec_port = ProposalRecorder(find_pair_port)
request_rec_port = RequestRecorder(find_pair_port)

print "Car Pooling Server is now runing"
