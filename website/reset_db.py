from django.contrib.auth.models import User

from profiles.models import *
from evaluations.models import *
from requests.models import *
from offers.models import *
from proposals.models import *
from rides.models import *

User.objects.all().delete()
UserProfile.objects.all().delete()
Evaluation.objects.all().delete()
Request.objects.all().delete()
Offer.objects.all().delete()
Proposal.objects.all().delete()
Ride.objects.all().delete()

user = User.objects.create_user('mart', 'mart@mart.net', 'martin')
user.is_superuser = True
user.save()
