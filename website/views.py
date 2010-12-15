from django.shortcuts import render_to_response, redirect
from django import forms
from django.contrib import auth

from django.core.context_processors import csrf
from django.template import RequestContext
from django.core.mail import send_mail


import datetime

class LoginForm(forms.Form):
    login = forms.CharField(max_length=50,
                       error_messages={'required': 'Login requiered'})
    password = forms.CharField(max_length=50,
                       widget=forms.PasswordInput(render_value=False),
                       error_messages={'required': 'Password requiered'}) 


def home(request):
    current_date = datetime.datetime.now()
    if request.user.is_authenticated():
        connected = True
        name = request.user.username
    else:
        if request.method == 'POST':
            form = LoginForm(request.POST)
            if form.is_valid():
                username = request.POST.get('login', '')
                passwd = request.POST.get('password', '')
                user = auth.authenticate(username=username, password=passwd)
                if user is not None and user.is_active:
                    auth.login(request, user)
                    connected = True
                    name = request.user.username
                    notifications = [{'error':False, 'content':'You are now connected'}]
                else:
                    connected = False
                    notifications = [{'error':True, 'content':'Incorrect login or password'}]
            else:
                connected = False
                notifications = [{'error':True, 'content':'Invalid form'}]
        else:
            connected = False
            form = LoginForm(initial={'login': 'login'})

            return render_to_response('home.html', locals())

    return render_to_response('home.html', locals())
    

    
def hello(request):
    send_mail('test subject', "ceci est un beau email de test", "testfake@email.com", ["mart.tri@gmail.com"])
    return render_to_response('hello.html', locals())


def logout(request):
    auth.logout(request)
    connected = False
    form = LoginForm(initial={'login': 'login'})
    notifications = [{'error':False, 'msg':'You are now disconnected'}]
    return redirect('/home/')

