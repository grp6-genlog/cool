from django.shortcuts import render_to_response

from website.profiles.models import UserProfile
from website.requests.models import Request
from django.contrib.auth.models import User

def myrequests(request):
    if not request.user.is_authenticated():
        return render_to_response('home.html', locals())
    
    user=UserProfile.objects.get(user=request.user)
    requests = user.request_set.all()
    return render_to_response('myrequests.html', locals())
    
def addrequest(request):
    if not request.user.is_authenticated():
        return render_to_response('home.html', locals())
        
    
