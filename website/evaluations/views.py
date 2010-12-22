from django.shortcuts import render_to_response, redirect
from django.http import HttpResponseRedirect
from django import forms

from website.profiles.models import UserProfile
from website.evaluations.models import Evaluation
from website.rides.models import Ride
from django.contrib.auth.models import User

from portobject import *
from guiutils import WaitCallbacks

import datetime, time


RATING_CHOICES = (
    (1, '1/5'),
    (2, '2/5'),
    (3, '3/5'),
    (4, '4/5'),
    (5, '5/5'),
)

class EvaluationForm(forms.Form):
    rating = forms.ChoiceField(choices=RATING_CHOICES, initial=3)
    content = forms.CharField(max_length=500,
                            widget=forms.Textarea,
                            required=False)



class WaitCallbacksEval(WaitCallbacks):
    pass


def myevaluations(request):
    if not request.user.is_authenticated():
        return redirect('/home/')
    
    user_p = UserProfile.objects.get(user=request.user)
    evaluation_l = Evaluation.objects.filter(user_to=user_p)
    
    return render_to_response('myevaluations.html', locals())
    
    
    
def addevaluation(request, offset, port_evaluation=None):
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
        
            if request.method == 'POST':
                form = EvaluationForm(request.POST)
                if form.is_valid():
                    form.cleaned_data
                    
                    rating = form.cleaned_data['rating']
                    content = form.cleaned_data['content']
                    
                    WaitCallbacksEval.declare(request.user)
                    
                    anonymous_send_to(port_evaluation,('evaluate', offset, UserProfile.objects.get(user=request.user).id,
                                                                  (rating, content),
                                                        lambda:successcall(request.user),
                                                        lambda:failurecall(request.user)))
                    
                    wait_counter = 0
                    while WaitCallbacksEval.is_pending(request.user) and wait_counter < 10:
                        time.sleep(0.1)
                        wait_counter += 1
                    
                    if WaitCallbacksEval.status(request.user) == 'success':
                        WaitCallbacksEval.free(request.user)
                        notification = {'content':'Evaluation successfully registered', 'success':True}
                        return render_to_response('home.html', locals())
                    else:
                        print WaitCallbacksEval.status(request.user)
                        WaitCallbacksEval.free(request.user)
                        notification = {'content':'An error occured, try again later', 'success':False}
                        return render_to_response('evaluationform.html', locals())
                else:
                    return render_to_response('evaluationform.html', locals())
            else:
              
                if ride.offer.status != 'F' and ride.offer.status != 'C':
                    notification = {'content':'Invalid call, ride not done or cancelled', 'success':False}
                    return render_to_response('home.html', locals())
                
                if request.user == ride.offer.proposal.user.user:
                    user_to = ride.offer.request.user
                elif request.user == ride.offer.request.user.user:
                    user_to = ride.offer.proposal.user
                else:
                    notification = {'content':'Invalid call, you have not participated to this ride', 'success':False}
                    return render_to_response('home.html', locals())
                
                evaluation = Evaluation.objects.filter(ride=ride, user_to=user_to)
                if len(evaluation) != 1:
                    notification = {'content':'You can not evaluate this ride', 'success':False}
                    return render_to_response('home.html', locals())
                evaluation = evaluation[0]
                
                if evaluation.locked:
                    notification = {'content':'You can not evaluate this ride anymore', 'success':False}
                    return render_to_response('home.html', locals())
                
                init = {
                    'rating' : evaluation.rating,
                    'content' : evaluation.content,
                }
                form = EvaluationForm(initial = init)
                return render_to_response('evaluationform.html', locals())
                    
                    

def successcall(user):
    WaitCallbacksEval.update(user, 'success')
    
def failurecall(user):
    WaitCallbacksEval.update(user, 'fail')
        
