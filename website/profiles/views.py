from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect

from django import forms
from django.contrib import auth
from django.core.context_processors import csrf
from django.template import RequestContext
from django.contrib.admin import widgets
from django.db import models


from website.profiles.models import UserProfile
from django.contrib.auth.models import User

import datetime, time

from portobject import PortObject
from guiutils import WaitCallbacks

gui_port = PortObject()

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


class EditProfileForm(forms.Form):
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


class PasswordForm(forms.Form):
    old_password = forms.CharField(max_length=50,
                       min_length=3,
                       widget=forms.PasswordInput(render_value=False),)
    new_password = forms.CharField(max_length=50,
                       min_length=3,
                       widget=forms.PasswordInput(render_value=False),)
    new_password2 = forms.CharField(max_length=50,
                       widget=forms.PasswordInput(render_value=False),
                       label=u'Confirm password')



class WaitCallbacksProfile(WaitCallbacks):
    pass


def register(request, port_profile=None):
    
    if request.user.is_authenticated():
        connected = True
        name = request.user.username
        return render_to_response('home.html', locals())
    else:
        action = "Register"
        if request.method == 'POST':
            form = RegisterForm(request.POST)
               
            valid = form.is_valid()
            
            usern = request.POST.get('username', '')
            if User.objects.filter(username=usern):
                form._errors["username"] = form.error_class(["There is already a user with that username"])
                valid = False
            
            passwd = request.POST.get('password', '')
            passwd2 = request.POST.get('password2', '')
            if passwd != passwd2:
                form._errors["password"] = form.error_class(["The two passwords are different"])
                valid = False
            
            email_addr = request.POST.get('email', '')
            if User.objects.filter(email=email_addr):
                form._errors["email"] = form.error_class(["This email address is already used by another user"])
                valid = False
                
            if valid:
                return toprofilerecorder(request,port_profile,'register')
                
            else:
                return render_to_response('register.html', locals())
        else:
            form = RegisterForm(initial={'date_of_birth': datetime.date.today()})
            return render_to_response('register.html', locals())


def editprofile(request, port_profile=None):
    if not request.user.is_authenticated():
        current_date = datetime.datetime.now()
        return render_to_response('home.html', locals())
        
    else:
        try:
            p = UserProfile.objects.get(user=request.user)
        except:
            return render_to_response('404.html', locals())
        else:
            action = "Edit"
            
            if request.method == 'POST':
                form = EditProfileForm(request.POST)
               
                valid = form.is_valid()
                
                email_addr = form.cleaned_data['email']
                if request.user.email != email_addr and User.objects.filter(email=email_addr):
                    form._errors["email"] = form.error_class(["This email address is already used by another user"])
                    valid = False
                    
                if valid:
                    return toprofilerecorder(request,port_profile,'edit')
            
            else:
                init = {
                    'email' : request.user.email,
                    'first_name' : request.user.first_name,
                    'last_name' : request.user.last_name,
                    'date_of_birth' : p.date_of_birth,
                    'smoker' : p.smoker,
                    'gender' : p.gender,
                    'communities' : p.communities,
                    'money_per_km' : p.money_per_km,
                    'bank_account_number' : p.bank_account_number,
                    'phone_number' : p.phone_number,
                    'car_id' : p.car_id,
                    'car_description' : p.car_description,
                    'number_of_seats' : p.number_of_seats,
                }
                form = EditProfileForm(initial=init,)

            return render_to_response('register.html', locals())
            
def changepassword(request, port_profile=None):
    if not request.user.is_authenticated():
        current_date = datetime.datetime.now()
        return render_to_response('home.html', locals())
    
    else:
        try:
            p = UserProfile.objects.get(user=request.user)
        except:
            return render_to_response('404.html', locals())
        else:
            action = "password" 
            if request.method == 'POST':
                form = PasswordForm(request.POST)
               
                valid = form.is_valid()
                
                old_p = form.cleaned_data['old_password']
                new_p1 = form.cleaned_data['new_password']
                new_p2 = form.cleaned_data['new_password2']
                
                if auth.models.check_password(old_p, request.user.password):
                    form._errors["old_p"] = form.error_class(["Invalid password"])
                    valid = False
                
                if new_p1 != new_p2:
                    form._errors["new_p2"] = form.error_class(["The passwords don't match"])
                    valid = False
                    
                if valid:
                    request.user.set_password(new_p1)
                    notifications = "Password changed"
                    return render_to_response('home.html', locals())
            
            else:
                form = PasswordForm()

            return render_to_response('home.html', locals())
    
        
def toprofilerecorder(request, port_profile, action):
    if action != 'register' and action != 'edit':
        return render_to_response('404.html', locals())
        
    if action == 'register':
        form = RegisterForm(request.POST)
    elif action == 'edit':
        form = EditProfileForm(request.POST)
    form.is_valid()
    form.cleaned_data
    
    if action == 'register':
        username = form.cleaned_data['username']
        pwd = form.cleaned_data['password']
        email = form.cleaned_data['email']
        n_user = User.objects.create_user(username, email, pwd)
        
    elif action == 'edit':
        email = form.cleaned_data['email']
        n_user = request.user
        n_user.email = email
    
    n_user.first_name = form.cleaned_data['first_name']
    n_user.last_name = form.cleaned_data['last_name']
    n_user.save()
        
    
    
    UserID = n_user.id
    NumberOfSeats = form.cleaned_data['number_of_seats']
    if not NumberOfSeats:
        NumberOfSeats = 0
    BirthDate = form.cleaned_data['date_of_birth']
    Smoker = form.cleaned_data['smoker']
    Communities = form.cleaned_data['communities']
    MoneyPerKm = form.cleaned_data['money_per_km']
    Gender = form.cleaned_data['gender']
    BankAccountNumber = form.cleaned_data['bank_account_number']
    CarID = form.cleaned_data['car_id']

    GSMNumber = form.cleaned_data['phone_number']
    CarDescription = form.cleaned_data['car_description']
        
    if action == 'register':
        msg = 'recordprofile'
    elif action == 'edit':
        msg = 'updateprofile'
        
    WaitCallbacksProfile.declare(request.user)
    
    gui_port.send_to(port_profile,(msg,[n_user,NumberOfSeats,
                                       BirthDate,Smoker,Communities,MoneyPerKm,
                                       Gender,BankAccountNumber,CarID,
                                       GSMNumber,CarDescription],
                                   successcall,
                                   failurecall,
                                   request.user))
    wait_counter = 0
    while WaitCallbacksProfile.is_pending(request.user) and wait_counter < 10:
        time.sleep(0.1)
        wait_counter += 1
            
    if WaitCallbacksProfile.status(request.user) == 'success':
        WaitCallbacksProfile.free(request.user)
        if action == 'register':

            user = auth.authenticate(username=n_user.username, password=pwd)
            if user is not None and user.is_active:
                auth.login(request, user)

        return render_to_response('home.html', locals())
    else:
        print WaitCallbacksProfile.status(request.user)
        WaitCallbacksProfile.free(request.user)
        return render_to_response('error.html', locals())
            
    

def successcall(user):
    WaitCallbacksProfile.update(user, 'success')
    
def failurecall(user):
    WaitCallbacksProfile.update(user, 'fail')
