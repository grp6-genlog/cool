from django.shortcuts import render_to_response
from django.http import HttpResponse

from django import forms
from django.contrib import auth
from django.core.context_processors import csrf
from django.template import RequestContext
from django.contrib.admin import widgets
from django.db import models


from website.profiles.models import UserProfile
from django.contrib.auth.models import User

from website import PortObjects

import datetime


GENDER_CHOICES = (
    ('M', 'Male'),
    ('F', 'Female'),
)


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=50,
                                min_length=3)
    password = forms.CharField(max_length=50,
                       min_length=3,
                       widget=forms.PasswordInput(render_value=False),)
    password2 = forms.CharField(max_length=50,
                       widget=forms.PasswordInput(render_value=False),
                       label=u'Confirm password')
    email = forms.EmailField(max_length=70,
                        label=u'Email address')
    first_name = forms.CharField(max_length=50,)
    last_name = forms.CharField(max_length=50,)
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
            
            email_addr = request.POST.get('email', '')
            if len(User.objects.filter(email=email_addr))!=0:
                form._errors["email"] = form.error_class(["This email address is already used by another user"])
                valid = False
                
            if valid:
                toprofilerecorder(request,'register')
                notif = 'Registered !'

        else:
            form = RegisterForm(initial={'date_of_birth': datetime.date.today()})
        return render_to_response('register.html', locals())


def editprofile(request):
    if request.user.is_authenticated():
        connected = True
        name = request.user.username
        return render_to_response('index.html', locals())
    else:
        return redirect('/home')
        
        
def toprofilerecorder(request, action):
    if action == 'register':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        email = request.POST.get('email', '')
        
        n_user = User.objects.create_user(username, email, password)
        n_user.first_name = request.POST.get('first_name', '')
        n_user.last_name = request.POST.get('last_name', '')
        n_user.save()
        
        UserID = n_user.id
        NumberOfSeats = request.POST.get('number_of_seats', 0)
        BirthDate = request.POST.get('date_of_birth', 0)
        Smoker = request.POST.get('smoker', False)
        Communities = request.POST.get('communities', '')
        MoneyPerKm = request.POST.get('money_per_km', 0)
        Gender = request.POST.get('gender', 'M')
        BankAccountNumber = request.POST.get('bank_account_number', '')
        CarID = request.POST.get('car_id', '')
        GSMNumber = request.POST.get('phone_number', '')
        CarDescription = request.POST.get('car_description', '')
        SmartphoneID = request.POST.get('smartphone_id', '')
        
        PortObjects.profile_rec_port.put((None,('recordprofile',[UserID,NumberOfSeats,
                                                       BirthDate,Smoker,Communities,MoneyPerKm,
                                                       Gender,BankAccountNumber,CarID,
                                                       GSMNumber,CarDescription,SmartphoneID],
                                      None,
                                      None)))

