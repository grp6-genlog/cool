from django.shortcuts import render_to_response
from django import forms
from django.contrib import auth
from django.core.context_processors import csrf
from django.template import RequestContext
from django.contrib.admin import widgets

from website.profiles.models import UserProfile

import datetime

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=50,)
    password = forms.CharField(max_length=50,
                       widget=forms.PasswordInput(render_value=False),)
    password2 = forms.CharField(max_length=50,
                       widget=forms.PasswordInput(render_value=False),
                       label=u'Confirm password')
    email = forms.EmailField(max_length=70,
                        label=u'Email address')                                              
    number_of_seats = forms.IntegerField()
    date_of_birth = forms.DateField(widget=widgets.AdminDateWidget())
    smoker = forms.BooleanField()
    communities = forms.CharField(max_length=100)
    money_per_km = forms.FloatField()
    gender = forms.CharField(max_length=1)
    bank_account_number = forms.CharField(max_length=30)
    account_balance = forms.FloatField()
    car_id = forms.CharField(max_length=50,
                        label=u'Car plate number')
    phone_number = forms.CharField(max_length=20)
    car_description = forms.CharField(max_length=500,
                            widget=forms.Textarea,)
    smartphone_id = forms.CharField(max_length=100)

def register(request):
    
    if request.user.is_authenticated():
        connected = True
        name = request.user.username
        return render_to_response('index.html', locals())
    else:
        form = RegisterForm(initial={'date_of_birth': datetime.date.today()})
        return render_to_response('register.html', locals())
