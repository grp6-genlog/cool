from django.contrib.auth.models import User

from profiles.models import *
from evaluations.models import *
from requests.models import *
from offers.models import *
from proposals.models import *
from rides.models import *

print "emptying tables..."
User.objects.all().delete()
UserProfile.objects.all().delete()
Evaluation.objects.all().delete()
Request.objects.all().delete()
Offer.objects.all().delete()
Proposal.objects.all().delete()
Ride.objects.all().delete()

print "creating super user..."
user = User.objects.create_user('mart', 'mart.tri@gmail.com', 'martin')
user.is_superuser = True
user.is_staff = True
user.is_active = True
user.first_name = 'martin'
user.last_name ='trigaux'
user.save()
up = UserProfile()
up.user = user
up.gender = 'M'
up.bank_account_number = 'BE-123'
up.phone_number = '012345'
up.save()

#print "filling the tables..."
#import Fulfil
