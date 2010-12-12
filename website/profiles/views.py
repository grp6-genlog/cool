from django.shortcuts import render_to_response
from django import forms
from django.contrib import auth
from django.core.context_processors import csrf
from django.template import RequestContext
from django.contrib.admin import widgets
from django.db import models


from website.profiles.models import UserProfile
from django.contrib.auth.models import User

import datetime


GENDER_CHOICES = (
    ('M', 'Male'),
    ('F', 'Female'),
)


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=50,)
    password = forms.CharField(max_length=50,
                       widget=forms.PasswordInput(render_value=False),)
    password2 = forms.CharField(max_length=50,
                       widget=forms.PasswordInput(render_value=False),
                       label=u'Confirm password')
    email = forms.EmailField(max_length=70,
                        label=u'Email address')                                              
    date_of_birth = forms.DateField(widget=widgets.AdminDateWidget())
    smoker = forms.BooleanField(required=False)
    gender = forms.ChoiceField(choices=GENDER_CHOICES)
    communities = forms.CharField(max_length=100,
                        required=False)
    money_per_km = forms.FloatField(required=False)
    bank_account_number = forms.CharField(max_length=30)
    phone_number = forms.CharField(max_length=20)
    car_id = forms.CharField(max_length=10,
                        label=u'Car plate number',
                        required=False)
    car_description = forms.CharField(max_length=500,
                            widget=forms.Textarea,
                            required=False)
    number_of_seats = forms.IntegerField(required=False)
    smartphone_id = forms.CharField(max_length=100,
                                required=False)

def register(request):
    
    if request.user.is_authenticated():
        connected = True
        name = request.user.username
        return render_to_response('index.html', locals())
    else:
        if request.method == 'POST':
            form = RegisterForm(request.POST)
               
            valid = form.is_valid()
            
            usern = request.POST.get('username', '')
            if len(User.objects.filter(username=usern))!=0:
                form._errors["username"] = form.error_class(["There is already a user with that username"])
                valid = False
            
            passwd = request.POST.get('password', '')
            passwd2 = request.POST.get('password2', '')
            if passwd != passwd2:
                form._errors["password"] = form.error_class(["The two passwords are different"])
                valid = False
            
            if valid:
                #utils.toprofilerecorder(request,'register')
                notif = 'Registered !'

        else:
            form = RegisterForm(initial={'date_of_birth': datetime.date.today()})
        return render_to_response('register.html', locals())
