from django.shortcuts import render_to_response

from django import forms
from django.contrib import auth
from django.core.context_processors import csrf
from django.template import RequestContext
from django.contrib.admin import widgets
from django.db import models


from website.profiles.models import UserProfile
from website.offers.models import Offer
from website.requests.models import Request
from website.proposals.models import Proposal
from website.evaluations.models import Evaluation
from django.contrib.auth.models import User

import datetime, time

from portobject import *
from guiutils import *

# choices for the gender of the user
GENDER_CHOICES = (
    ('M', 'Male'),
    ('F', 'Female'),
)


""" Different fields to register a new user """
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


""" Different fields to modify the profile of a user """
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


""" Different fields to modify the password of a user """
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

""" Different fields to add money to the virtual account of the user """
class FillAccountForm(forms.Form):
    amount = forms.FloatField()
    password = forms.CharField(max_length=50,
                       min_length=3,
                       widget=forms.PasswordInput(render_value=False),)

""" Different fields to transfer money from the virtual account of the user
    to the specified bank account """
class TransferAccountForm(forms.Form):
    amount = forms.FloatField()
    account_number = forms.CharField(max_length=50,)
    password = forms.CharField(max_length=50,
                       min_length=3,
                       widget=forms.PasswordInput(render_value=False),)


class WaitCallbacksProfile(WaitCallbacks):
    pass


""" 
Return an HTML page with the response while trying to register a user
Redirect to the home page if a user is logged in or the call is invalid
If the registration form is not filled correctly, display an message explaining
the error.
If the profilerecorder didn't proccess the message correctly display an error
message, display a validation message otherwise.
request : request object created by django at the function call
port_profile : port object to the profile recorder
@pre : /
@post : the registration is send to the registration recorder to be stored in 
    the database
""" 
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


""" 
Return an HTML page with the response while trying to edit the profile of a user
Redirect to the home page if no user is logged in or the call is invalid
If the edition form is not filled correctly, display an message explaining
the error.
If the profilerecorder didn't proccess the message correctly display an error
message, display a validation message otherwise.
request : request object created by django at the function call
port_profile : port object to the profile recorder
@pre : /
@post : the modifications are send to the registration recorder to be stored in 
    the database
""" 
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

                if form.is_valid():
                    
                    form.cleaned_data            
                    email_addr = form.cleaned_data['email']
                    if request.user.email != email_addr and User.objects.filter(email=email_addr):
                        form._errors["email"] = form.error_class(["This email address is already used by another user"])
                    else:
                        
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
   
   
""" 
Return an HTML page with the response while trying to change the password of a user
Redirect to the home page if no user is logged in or the call is invalid
If request.POST is false, display the empty password form
If the change password form is not filled correctly, display an message
explaining the error.
If the profilerecorder didn't proccess the message correctly display an error
message, display a validation message otherwise.
request : request object created by django at the function call
port_profile : port object to the profile recorder
@pre : /
@post : the change is send to the registration recorder to be stored in 
    the database
"""
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
                
                if not auth.models.check_password(old_p, request.user.password):
                    form._errors["old_password"] = form.error_class(["Invalid password"])
                    valid = False
                
                if new_p1 != new_p2:
                    form._errors["new_password2"] = form.error_class(["The passwords don't match"])
                    valid = False
                    
                if valid:
                    
                    return toprofilerecorder(request,port_profile,'password')
            
            else:
                form = PasswordForm()

            return render_to_response('password.html', locals())
    

"""
Send a message to the profile recorder. A form associated to the action is
in send via POST in the request object
request : request object created by django at the function call
port_profile : port object to the profile recorder
action : 'register' (RegisterForm), 'edit' (EditProfileForm) or 'password' (PasswordForm)
"""
def toprofilerecorder(request, port_profile, action):
    if action != 'register' and action != 'edit' and action != 'password':
        return render_to_response('home.html', locals())

    if action == 'register':
        form = RegisterForm(request.POST)
    elif action == 'edit':
        form = EditProfileForm(request.POST)
    elif action == 'password':
        form = PasswordForm(request.POST)
    
    form.is_valid()
    form.cleaned_data
    
    
        
    if action == 'register':
        username = form.cleaned_data['username']
        pwd = form.cleaned_data['password']
    else:
        username = request.user.username
        
    if action == 'password':
        pwd = form.cleaned_data['new_password']
    else:
        email = form.cleaned_data['email']
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        
        BirthDate = form.cleaned_data['date_of_birth']
        Smoker = form.cleaned_data['smoker']
        Communities = form.cleaned_data['communities']
        MoneyPerKm = form.cleaned_data['money_per_km']
        Gender = form.cleaned_data['gender']
        BankAccountNumber = form.cleaned_data['bank_account_number']
        GSMNumber = form.cleaned_data['phone_number']
        
        CarID = form.cleaned_data['car_id']
        CarDescription = form.cleaned_data['car_description']
        NumberOfSeats = form.cleaned_data['number_of_seats']
        if not NumberOfSeats:
            NumberOfSeats = 0
    
    WaitCallbacksProfile.declare(request.user)
    
    if action == 'register':
        anonymous_send_to(port_profile,('recordprofile',[username, pwd, email,
                                                        first_name, last_name, NumberOfSeats,
                                                        BirthDate, Smoker, Communities,
                                                        MoneyPerKm, Gender, BankAccountNumber,
                                                        CarID, GSMNumber, CarDescription],
                                   lambda:successcall(request.user),
                                   lambda:failurecall(request.user)))
        
    elif action == 'edit':
        anonymous_send_to(port_profile,('updateprofile',[request.user.id, None, email,
                                                        first_name, last_name, NumberOfSeats,
                                                        BirthDate, Smoker, Communities,
                                                        MoneyPerKm, Gender, BankAccountNumber,
                                                        CarID, GSMNumber, CarDescription],
                                   lambda:successcall(request.user),
                                   lambda:failurecall(request.user)))
    elif action == 'password':
        anonymous_send_to(port_profile,('changepass',[request.user.id, pwd],
                                   lambda:successcall(request.user),
                                   lambda:failurecall(request.user)))
    
    wait_counter = 0
    while WaitCallbacksProfile.is_pending(request.user) and wait_counter < 10:
        time.sleep(0.1)
        wait_counter += 1
            
    if WaitCallbacksProfile.status(request.user) == 'success':
        WaitCallbacksProfile.free(request.user)
        if action == 'register':
            user = auth.authenticate(username=username, password=pwd)
            if user is not None and user.is_active:
                auth.login(request, user)

            notification = {'content':"Account registered successfully", 'success':True}
        elif action == 'updateprofile':
            notification = {'content':'Your profile has been updated', 'success':True}
        elif action == 'password':
            notification = {'content':"Password changed successfully", 'success':True}
        return render_to_response('home.html', locals())
    else:
        WaitCallbacksProfile.free(request.user)
        notification = {'content':'Unexpected error, try again later', 'success':True}
        return render_to_response('home.html', locals())
    

""" 
Return an HTML page with the profile of the specified user displaying the
information that the connected user can see
Redirect to the home page if he isn't logged in
offset : id of the user specified in the url
""" 
def publicprofile(request, offset):
    try:
        offset = int(offset)
    except:
        notification = {'content':'Not an user', 'success':False}
        return render_to_response('home.html', locals())
    
    if not request.user.is_authenticated():
        current_date = datetime.datetime.now()
        notification = {'content':'Please log in to see this page', 'success':False}
        return render_to_response('home.html', locals())
    
    user_p = UserProfile.objects.get(user=request.user)    
    try:
        other = UserProfile.objects.get(user=User.objects.get(id=offset))
    except:
        notification = {'content':'Not an user', 'success':False}
        return render_to_response('home.html', locals())
    
    
    other_requests = Request.objects.filter(user=other)
    other_proposals = Proposal.objects.filter(user=other)
    user_requests = Request.objects.filter(user=user_p)
    user_proposals = Proposal.objects.filter(user=user_p)
    
    b = False
    for other_r in other_requests:
        other_offers = other_r.offer_set.all()
        for other_o in other_offers:
            if ((other_o.proposal in user_proposals) and other_o.status != 'D'):
                b = True
                com_offer = other_o
                break
        if b:
            break
    if not b:        
        for other_p in other_proposals:
            other_offers = other_p.offer_set.all()
            for other_o in other_offers:
                if ((other_o.request in user_requests) and other_o.status != 'D'):
                    b = True
                    com_offer = other_o
                    break
            if b:
                break
    if not b:
        notification = {'content':'You are not allowed to see this profile', 'success':False}
        return render_to_response('home.html', locals())
    else:
        age = int(abs(datetime.date.today() - other.date_of_birth).days/(365*0.75 + 366*0.25))
        evaluation_l = other.user_to.all()
        return render_to_response('publicprofile.html', locals())

        
""" 
Return an HTML page with the response while trying to add money to the account of a user
Redirect to the home page if no user is logged in or the call is invalid
If request.POST is false, display the empty fillaccountform and transferaccountform
If the form is not filled correctly, display an message explaining the error.
If the payement manager didn't proccess the message correctly display an error
message, display a validation message otherwise.
request : request object created by django at the function call
port_payement : port object to the payement manager
@pre : /
@post : the change is send to the payement manager to be stored in 
    the database
"""
def myaccount(request, port_payment):
    if not request.user.is_authenticated():
        current_date = datetime.datetime.now()
        notification1 = {'content':'Please log in to see this page', 'success':False}
        return render_to_response('home.html', locals())
    
    user_p = UserProfile.objects.get(user=request.user)
    
    current_amount = user_p.account_balance
    form1 = FillAccountForm()
    init = { 'account_number' : user_p.bank_account_number }
    form2 = TransferAccountForm(initial = init)
    
    if request.method == 'POST':
        form1 = FillAccountForm(request.POST)
        
        if form1.is_valid():
            amount = form1.cleaned_data['amount']
            
            if amount <= 0:                
                form1._errors["amount"] = form1.error_class(["Insert a positive amount"])
                return render_to_response('accountform.html', locals())
            
            pwd = form1.cleaned_data['password']
            if not auth.models.check_password(pwd, request.user.password):
                form1._errors["password"] = form1.error_class(["Invalid password"])
                return render_to_response('accountform.html', locals())
            
            communication = "Carpooling transfer from "+request.user.first_name+" "+request.user.last_name
            WaitCallbacksProfile.declare(request.user)
    
            anonymous_send_to(port_payment,('addmoney',(user_p.id,
                                                user_p.bank_account_number,
                                                communication,
                                                amount),
                                           lambda:successcall(request.user),
                                           lambda:failurecall(request.user)))
            wait_counter = 0
            while WaitCallbacksProfile.is_pending(request.user) and wait_counter < 10:
                time.sleep(0.1)
                wait_counter += 1
            
            user_p = UserProfile.objects.get(user=request.user)
            if WaitCallbacksProfile.status(request.user) == 'success':
                WaitCallbacksProfile.free(request.user)

                notification1 = {'content':'Your account has been filled with '+str(amount)+' euro', 'success':True}
                current_amount = user_p.account_balance
                return render_to_response('accountform.html', locals())
                
            else:
                WaitCallbacksProfile.free(request.user)
                notification1 = {'content':'Unexpected error, try again later', 'success':False}
                
                current_amount = user_p.account_balance
                return render_to_response('accountform.html', locals())
    else:
        current_amount = user_p.account_balance
        return render_to_response('accountform.html', locals())
        

""" 
Return an HTML page with the response while trying to transfer money from the account of a user
Redirect to the home page if no user is logged in or the call is invalid
If request.POST is false, display the empty fillaccountform and transferaccountform
If the form is not filled correctly, display an message explaining the error.
If the payement manager didn't proccess the message correctly display an error
message, display a validation message otherwise.
request : request object created by django at the function call
port_payement : port object to the payement manager
@pre : /
@post : the change is send to the payement manager to be stored in 
    the database
"""
def emptyaccount(request, port_payment):
    if not request.user.is_authenticated():
        current_date = datetime.datetime.now()
        notification2 = {'content':'Please log in to see this page', 'success':False}
        return render_to_response('home.html', locals())
    
    user_p = UserProfile.objects.get(user=request.user)    
    
    current_amount = user_p.account_balance
    form1 = FillAccountForm()
    init = { 'account_number' : user_p.bank_account_number }
    form2 = TransferAccountForm(initial = init)    
    
    if request.method == 'POST':
        form2 = TransferAccountForm(request.POST)
        
        if form2.is_valid():
            amount = form2.cleaned_data['amount']
            
            if amount <= 0:                
                form2._errors["amount"] = form2.error_class(["Insert a positive amount"])
                return render_to_response('accountform.html', locals())
            
            account_number = form2.cleaned_data['account_number']
            pwd = form2.cleaned_data['password']
            if not auth.models.check_password(pwd, request.user.password):
                form2._errors["password"] = form2.error_class(["Invalid password"])
                return render_to_response('accountform.html', locals())
                    
            WaitCallbacksProfile.declare(request.user)
    
            anonymous_send_to(port_payment,('getmoney',(user_p.id,
                                                    account_number,
                                                    amount),
                                           lambda:successcall(request.user),
                                           lambda:failurecall(request.user)))
            wait_counter = 0
            while WaitCallbacksProfile.is_pending(request.user) and wait_counter < 10:
                time.sleep(0.1)
                wait_counter += 1
            
            user_p = UserProfile.objects.get(user=request.user) 
            if WaitCallbacksProfile.status(request.user) == 'success':
                WaitCallbacksProfile.free(request.user)
                
                msg = str(amount)+' euro have been transfered to your account'
                notification2 = {'content': msg, 'success':True}
                current_amount = user_p.account_balance
                
                return render_to_response('accountform.html', locals())
                
            else:
                WaitCallbacksProfile.free(request.user)
                notification2 = {'content':'Unexpected error, try again later', 'success':False}
                
                current_amount = user_p.account_balance
                return render_to_response('accountform.html', locals())
    else:
        return render_to_response('accountform.html', locals())

        

"""
Success callback function
@post : update the callback dictionnary to set 'success' at the key with the user 
"""        
def successcall(user):
    WaitCallbacksProfile.update(user, 'success')
    
"""
Failure callback function
@post : update the callback dictionnary to set 'fail' at the key with the user 
""" 
def failurecall(user):
    WaitCallbacksProfile.update(user, 'fail')

