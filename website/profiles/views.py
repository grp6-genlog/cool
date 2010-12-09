from django.shortcuts import render_to_response

from django import forms
from django.contrib import auth

from django.core.context_processors import csrf
from django.template import RequestContext


import datetime



class RegisterForm(forms.Form):
    username = forms.CharField(max_length=50,
                       error_messages={'required': 'Username requiered'})
    password = forms.CharField(max_length=50,
                       widget=forms.PasswordInput(render_value=False),
                       error_messages={'required': 'Password requiered'})
    password2 = forms.CharField(max_length=50,
                       widget=forms.PasswordInput(render_value=False),
                       error_messages={'required': 'Password requiered'},
                       label=u'Confirm')
                                              
    number_of_seats = forms.IntegerField()
    date_of_birth = forms.DateField(widget=forms.DateInput())
    smoker = forms.BooleanField()
    communities = forms.CharField(max_length=100)
    money_per_km = forms.FloatField()
    gender = forms.CharField(max_length=1)
    bank_account_number = forms.CharField(max_length=30)
    account_balance = forms.FloatField()
    car_id = forms.CharField(max_length=50)
    phone_number = forms.CharField(max_length=20)
    car_description = forms.CharField(max_length=500)
    smartphone_id = forms.CharField(max_length=100)

def register(request):
    
    if request.user.is_authenticated():
        connected = True
        name = request.user.username
        return render_to_response('home.html', locals())
    else:
        form = RegisterForm()
        return render_to_response('register.html', locals())
